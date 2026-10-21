"""Tests for SGUCollection, the module every client uses to reach one SGU collection."""

from datetime import UTC, datetime

import pytest

from sgu_client.client.base import BaseClient
from sgu_client.client.collection import SGUCollection
from sgu_client.config import SGUConfig
from sgu_client.exceptions import SGUAmbiguousError, SGUClientError, SGUNotFoundError
from sgu_client.models.observed import (
    GroundwaterMeasurementCollection,
    GroundwaterStation,
    GroundwaterStationCollection,
)
from tests.mock_responses import (
    create_mock_empty_collection_response,
    create_mock_multiple_stations_response,
    create_mock_single_station_response,
)

ROOT = "https://example.test/oppnadata/"
DATASET_URL = f"{ROOT}grundvattennivaer-observerade/ogc/features/v1/"


@pytest.fixture
def base_client(fake):
    return BaseClient(config=SGUConfig(base_url=ROOT), transport=fake)


@pytest.fixture
def stations(base_client):
    return SGUCollection(
        base_client,
        dataset="grundvattennivaer-observerade",
        name="stationer",
        model=GroundwaterStationCollection,
        label="Station",
    )


def test_get_returns_the_feature_from_the_collection_url(fake, stations):
    fake.add("", create_mock_single_station_response())
    station = stations.get("stationer.4086")

    assert isinstance(station, GroundwaterStation)
    assert station.id == "stationer.4086"
    assert (
        fake.requests[-1].url
        == f"{DATASET_URL}collections/stationer/items/stationer.4086"
    )


def test_get_raises_not_found_when_no_feature_matches(fake, stations):
    fake.add("", create_mock_empty_collection_response())
    with pytest.raises(SGUNotFoundError, match="Station NOPE not found"):
        stations.get("NOPE")


def test_not_found_is_still_a_value_error():
    assert issubclass(SGUNotFoundError, ValueError)
    assert issubclass(SGUNotFoundError, SGUClientError)


def test_get_raises_ambiguous_when_several_features_match(fake, stations):
    fake.add("", create_mock_multiple_stations_response())
    with pytest.raises(
        SGUAmbiguousError, match="Multiple stations returned for ID stationer.4086"
    ):
        stations.get("stationer.4086")


def test_ambiguous_is_still_a_value_error():
    assert issubclass(SGUAmbiguousError, ValueError)
    assert issubclass(SGUAmbiguousError, SGUClientError)


def test_query_returns_the_collection_and_encodes_params(fake, stations):
    fake.add("", create_mock_multiple_stations_response())
    result = stations.query(
        bbox=[12.0, 55.0, 16.0, 58.0],
        sortby=["+datum", "-omrade_id"],
        limit=100,
        datetime="2024-08-01Z",
        filter_expr="kommun='Mora'",
        properties="obsplatsnamn",
    )

    assert isinstance(result, GroundwaterStationCollection)
    assert len(result.features) == 2
    assert fake.requests[-1].url == f"{DATASET_URL}collections/stationer/items"
    assert fake.params == {
        "bbox": "12.0,55.0,16.0,58.0",
        "sortby": "+datum,-omrade_id",
        "limit": 100,
        "datetime": "2024-08-01Z",
        "filter": "kommun='Mora'",
        "properties": "obsplatsnamn",
    }


def test_query_leaves_out_params_that_are_not_given(fake, stations):
    fake.add("", create_mock_empty_collection_response())
    stations.query(limit=10, bbox=None, datetime=None)

    assert fake.params == {"limit": 10}


@pytest.mark.parametrize(
    ("where", "expected"),
    [
        ({"platsbeteckning": "95_2"}, "platsbeteckning='95_2'"),
        ({"nationellt_provplatsid": 359366}, "nationellt_provplatsid=359366"),
        ({"platsbeteckning": ["95_2"]}, "platsbeteckning='95_2'"),
        (
            {"platsbeteckning": ["TTK-442-M", "SYD-681-C"]},
            "platsbeteckning in ('TTK-442-M', 'SYD-681-C')",
        ),
        (
            {"nationellt_provplatsid": [359366, 378865]},
            "nationellt_provplatsid in (359366, 378865)",
        ),
        (
            {"parameternamn": "Bly", "nationellt_provplatsid": 359366},
            "parameternamn='Bly' AND nationellt_provplatsid=359366",
        ),
    ],
)
def test_query_where_builds_the_filter(fake, stations, where, expected):
    fake.add("", create_mock_empty_collection_response())
    stations.query(where=where)

    assert fake.params["filter"] == expected


def test_query_where_is_combined_with_a_raw_filter(fake, stations):
    fake.add("", create_mock_empty_collection_response())
    stations.query(where={"platsbeteckning": "95_2"}, filter_expr="kommun='Mora'")

    assert fake.params["filter"] == "platsbeteckning='95_2' AND kommun='Mora'"


def test_query_where_escapes_single_quotes(fake, stations):
    fake.add("", create_mock_empty_collection_response())
    stations.query(where={"obsplatsnamn": ["O'Brien", "Lagga_2"]})

    assert fake.params["filter"] == "obsplatsnamn in ('O''Brien', 'Lagga_2')"


@pytest.fixture
def measurements(base_client):
    return SGUCollection(
        base_client,
        dataset="grundvattennivaer-observerade",
        name="nivaer",
        model=GroundwaterMeasurementCollection,
        label="Measurement",
        date_field="obsdatum",
    )


TMIN = datetime(2020, 1, 1, tzinfo=UTC)
TMAX = datetime(2021, 1, 1, tzinfo=UTC)


@pytest.mark.parametrize(
    ("tmin", "tmax", "expected"),
    [
        (
            TMIN,
            TMAX,
            "obsdatum >= '2020-01-01T00:00:00+00:00'"
            " AND obsdatum <= '2021-01-01T00:00:00+00:00'",
        ),
        (TMIN, None, "obsdatum >= '2020-01-01T00:00:00+00:00'"),
        (None, TMAX, "obsdatum <= '2021-01-01T00:00:00+00:00'"),
        (
            "2020-01-01T00:00:00Z",
            "2021-01-01T00:00:00Z",
            "obsdatum >= '2020-01-01T00:00:00Z' AND obsdatum <= '2021-01-01T00:00:00Z'",
        ),
    ],
)
def test_query_filters_on_the_date_field(fake, measurements, tmin, tmax, expected):
    fake.add("", create_mock_empty_collection_response())
    measurements.query(tmin=tmin, tmax=tmax)

    assert fake.params["filter"] == expected


def test_query_without_dates_sends_no_filter(fake, measurements):
    fake.add("", create_mock_empty_collection_response())
    measurements.query(tmin=None, tmax=None)

    assert "filter" not in fake.params


def test_query_puts_where_first_then_dates_then_raw_filter(fake, measurements):
    fake.add("", create_mock_empty_collection_response())
    measurements.query(
        where={"platsbeteckning": "95_2"}, tmin=TMIN, filter_expr="metod='x'"
    )

    assert fake.params["filter"] == (
        "platsbeteckning='95_2'"
        " AND obsdatum >= '2020-01-01T00:00:00+00:00'"
        " AND metod='x'"
    )


def test_query_rejects_dates_on_a_collection_without_a_date_field(stations):
    with pytest.raises(ValueError, match="stationer has no date field"):
        stations.query(tmin=TMIN)


def test_find_one_returns_the_single_match(fake, stations):
    fake.add("", create_mock_single_station_response())
    station = stations.find_one(where={"obsplatsnamn": "Lagga_2"})

    assert isinstance(station, GroundwaterStation)
    assert fake.params["filter"] == "obsplatsnamn='Lagga_2'"


def test_find_one_raises_not_found_naming_the_filter(fake, stations):
    fake.add("", create_mock_empty_collection_response())
    with pytest.raises(
        SGUNotFoundError, match="No stations found for obsplatsnamn='Nope'"
    ):
        stations.find_one(where={"obsplatsnamn": "Nope"})


def test_find_one_raises_ambiguous_naming_the_filter(fake, stations):
    fake.add("", create_mock_multiple_stations_response())
    with pytest.raises(
        SGUAmbiguousError, match="Multiple stations found for obsplatsnamn='Dup'"
    ):
        stations.find_one(where={"obsplatsnamn": "Dup"})


def test_default_config_points_at_the_sgu_open_data_root(fake):
    stations = SGUCollection(
        BaseClient(transport=fake),
        dataset="grundvattennivaer-observerade",
        name="stationer",
        model=GroundwaterStationCollection,
        label="Station",
    )
    fake.add("", create_mock_empty_collection_response())
    stations.query()

    assert fake.requests[-1].url == (
        "https://api.sgu.se/oppnadata/grundvattennivaer-observerade"
        "/ogc/features/v1/collections/stationer/items"
    )


def test_query_rejects_a_raw_filter_param(stations):
    # it would silently replace the where/tmin/tmax conditions
    with pytest.raises(TypeError, match="filter_expr"):
        stations.query(where={"platsbeteckning": "95_2"}, filter="kommun='Mora'")
