"""Tests for automatic pagination, through the public client and a fake transport."""

import pytest

from sgu_client import SGUAPIError, SGUClient, TransportResponse
from tests.fakes import FakeTransport, paged
from tests.mock_responses import create_mock_modeled_area_feature

STATIONS = "collections/stationer/items"


def stations(start: int, count: int) -> list[dict]:
    """Minimal station features, numbered from start."""
    return [
        {
            "type": "Feature",
            "id": f"stationer.{i}",
            "geometry": None,
            "properties": {"rowid": i},
        }
        for i in range(start, start + count)
    ]


def ids(collection) -> list[int]:
    return [station.properties.row_id for station in collection.features]


@pytest.fixture
def fake():
    return FakeTransport()


@pytest.fixture
def client(fake):
    return SGUClient(transport=fake)


def test_no_pagination_needed(fake, client):
    fake.add(STATIONS, *paged(stations(1, 100), page_size=100))

    result = client.levels.observed.get_stations()

    assert len(result.features) == 100
    assert len(fake.requests) == 1


def test_fetches_every_page_in_order(fake, client):
    fake.add(STATIONS, *paged(stations(1, 250), page_size=100))

    result = client.levels.observed.get_stations(limit=250)

    assert ids(result) == list(range(1, 251))
    assert result.numberReturned == 250
    assert [(r.params.get("startIndex"), r.params["limit"]) for r in fake.requests] == [
        (None, 250),
        (100, 150),
        (200, 50),
    ]


def test_pages_without_a_limit_keep_the_first_page_size(fake, client):
    fake.add(STATIONS, *paged(stations(1, 15), page_size=10))

    result = client.levels.observed.get_stations()

    assert len(result.features) == 15
    # the last page is cut to what's left: 15 - 10
    assert fake.requests[1].params == {"startIndex": 10, "limit": 5}


def test_stops_at_the_user_limit(fake, client):
    first, second = paged(stations(1, 200), page_size=100, number_matched=1000)
    fake.add(STATIONS, first, {**second, "features": second["features"][:50]})

    result = client.levels.observed.get_stations(limit=150)

    assert len(result.features) == 150
    assert result.numberReturned == 150
    assert result.numberMatched == 1000
    assert fake.requests[1].params == {"startIndex": 100, "limit": 50}


def test_a_user_limit_above_50k_is_honoured(fake, client):
    first, second = paged(stations(1, 60000), page_size=50000, number_matched=8000000)
    fake.add(STATIONS, first, second)

    result = client.levels.observed.get_stations(limit=60000)

    assert len(result.features) == 60000
    assert fake.requests[1].params == {"startIndex": 50000, "limit": 10000}


def test_stops_at_50k_without_a_user_limit(fake, client):
    fake.add(STATIONS, paged(stations(1, 50000), 50000, number_matched=8000000)[0])

    result = client.levels.observed.get_stations()

    assert len(result.features) == 50000
    assert len(fake.requests) == 1


def test_does_not_page_when_sgu_does_not_count_matches(fake, client):
    page = {
        "type": "FeatureCollection",
        "features": [create_mock_modeled_area_feature()],
        "numberReturned": 1,
    }
    fake.add("collections/omraden/items", {**page, "totalFeatures": "unknown"})

    result = client.levels.modeled.get_areas()

    assert len(result.features) == 1
    assert len(fake.requests) == 1


def test_does_not_page_without_a_match_count(fake, client):
    page = paged(stations(1, 10), page_size=10)[0]
    del page["numberMatched"], page["totalFeatures"]
    fake.add(STATIONS, page)

    result = client.levels.observed.get_stations()

    assert len(result.features) == 10
    assert len(fake.requests) == 1


def test_keeps_the_first_page_metadata(fake, client):
    first, second = paged(stations(1, 150), page_size=100)
    first["timeStamp"] = "2024-05-01T12:00:00Z"
    fake.add(STATIONS, first, second)

    result = client.levels.observed.get_stations()

    assert result.timeStamp is not None
    assert result.timeStamp.isoformat().startswith("2024-05-01T12:00:00")
    assert result.numberReturned == 150


def test_stops_on_an_empty_page(fake, client):
    first = paged(stations(1, 100), page_size=100, number_matched=200)[0]
    empty = paged([], page_size=100, number_matched=200)[0]
    fake.add(STATIONS, first, empty)

    result = client.levels.observed.get_stations(limit=200)

    assert len(result.features) == 100
    assert len(fake.requests) == 2


def test_a_failing_later_page_raises(fake, client):
    first = paged(stations(1, 100), page_size=100, number_matched=200)[0]
    fake.add(STATIONS, first, TransportResponse(500, "Internal Server Error"))

    with pytest.raises(
        SGUAPIError, match="Pagination request failed with status 500"
    ) as e:
        client.levels.observed.get_stations()

    assert e.value.status_code == 500
    assert e.value.response_data == {"error": "Internal Server Error"}
