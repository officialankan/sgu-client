"""Tests for IdentifierLookup, which finds stations or sampling sites by identifier."""

import pytest

from sgu_client.client.base import BaseClient
from sgu_client.client.collection import SGUCollection
from sgu_client.client.identifiers import IdentifierLookup
from sgu_client.config import SGUConfig
from sgu_client.exceptions import SGUAmbiguousError, SGUNotFoundError
from sgu_client.models.observed import GroundwaterStationCollection
from tests.mock_responses import (
    create_mock_station_collection_response,
    create_mock_station_feature,
)

ROOT = "https://example.test/oppnadata/"


@pytest.fixture
def stations(fake):
    base_client = BaseClient(config=SGUConfig(base_url=ROOT), transport=fake)
    collection = SGUCollection(
        base_client,
        dataset="grundvattennivaer-observerade",
        name="stationer",
        model=GroundwaterStationCollection,
        label="Station",
    )
    return IdentifierLookup(
        collection,
        {
            "station_id": ("platsbeteckning", "station_id"),
            "station_name": ("obsplatsnamn", "station_name"),
        },
        ref="station_id",
        noun="station",
    )


def stations_response(*names: tuple[str, str]):
    """A stations response with one station per (station_id, station_name)."""
    return create_mock_station_collection_response(
        [
            create_mock_station_feature(
                station_id=f"stationer.{i}", platsbeteckning=sid, obsplatsnamn=name
            )
            for i, (sid, name) in enumerate(names)
        ]
    )


def test_find_one_returns_the_station_with_that_name(fake, stations):
    fake.add("", stations_response(("95_2", "Lagga_2")))

    station = stations.find_one({"station_id": None, "station_name": "Lagga_2"})

    assert station.properties.station_id == "95_2"
    assert fake.params["filter"] == "obsplatsnamn='Lagga_2'"


@pytest.mark.parametrize(
    "ids",
    [
        {"station_id": None, "station_name": None},
        {"station_id": "95_2", "station_name": "Lagga_2"},
        {"station_id": [], "station_name": None},
    ],
    ids=["none", "both", "empty list"],
)
def test_find_one_requires_exactly_one_identifier(fake, stations, ids):
    with pytest.raises(
        ValueError,
        match="Exactly one of 'station_id' or 'station_name' must be provided.",
    ):
        stations.find_one(ids)

    assert fake.requests == []


def test_find_one_raises_not_found_when_no_station_has_that_name(fake, stations):
    fake.add("", stations_response())

    with pytest.raises(
        SGUNotFoundError, match=r"No stations found for station_name: \['typo'\]"
    ):
        stations.find_one({"station_id": None, "station_name": "typo"})


def test_find_one_raises_ambiguous_when_several_stations_share_the_name(fake, stations):
    fake.add("", stations_response(("95_2", "Lagga"), ("95_3", "Lagga")))

    with pytest.raises(
        SGUAmbiguousError, match="Multiple stations found for station_name: 'Lagga'"
    ):
        stations.find_one({"station_id": None, "station_name": "Lagga"})


def test_find_all_returns_every_requested_station(fake, stations):
    fake.add("", stations_response(("95_2", "Lagga_2"), ("101_1", "Ugglebo")))

    found = stations.find_all({"station_id": ["95_2", "101_1"], "station_name": None})

    assert [s.properties.station_id for s in found.features] == ["95_2", "101_1"]
    assert fake.params["filter"] == "platsbeteckning in ('95_2', '101_1')"


def test_find_all_raises_not_found_listing_the_missing_names(fake, stations):
    fake.add("", stations_response(("95_2", "Lagga_2")))

    with pytest.raises(
        SGUNotFoundError,
        match=r"No stations found for station_name: \['typo', 'typo2'\]",
    ):
        stations.find_all(
            {"station_id": None, "station_name": ["Lagga_2", "typo", "typo2"]}
        )


def test_find_all_requires_exactly_one_identifier(stations):
    with pytest.raises(ValueError, match="Exactly one of"):
        stations.find_all({"station_id": ["95_2"], "station_name": ["Lagga_2"]})


def test_refs_passes_station_ids_through_without_a_request(fake, stations, caplog):
    refs = stations.refs({"station_id": ["95_2", "101_1"], "station_name": None})

    assert refs == ["95_2", "101_1"]
    assert fake.requests == []
    assert "additional API request" not in caplog.text


def test_refs_looks_up_the_station_ids_of_station_names(fake, stations, caplog):
    fake.add("", stations_response(("95_2", "Lagga_2"), ("101_1", "Ugglebo")))

    refs = stations.refs({"station_id": None, "station_name": ["Lagga_2", "Ugglebo"]})

    assert refs == ["95_2", "101_1"]
    assert fake.params["filter"] == "obsplatsnamn in ('Lagga_2', 'Ugglebo')"
    assert (
        "Using 'station_name' requires an additional API request to look up the "
        "station(s). For better performance, use 'station_id' directly if available."
    ) in caplog.text


def test_refs_raises_not_found_for_a_missing_station_name(fake, stations):
    fake.add("", stations_response(("95_2", "Lagga_2")))

    with pytest.raises(SGUNotFoundError, match=r"station_name: \['typo'\]"):
        stations.refs({"station_id": None, "station_name": ["Lagga_2", "typo"]})


def test_refs_raises_when_a_looked_up_station_has_no_station_id(fake, stations):
    station = create_mock_station_feature(obsplatsnamn="Lagga_2")
    station["properties"]["platsbeteckning"] = None
    fake.add("", create_mock_station_collection_response([station]))

    with pytest.raises(ValueError, match="Station stationer.4086 has no station_id"):
        stations.refs({"station_id": None, "station_name": ["Lagga_2"]})


def test_refs_is_none_when_optional_and_no_identifier_is_given(fake, stations):
    assert (
        stations.refs({"station_id": None, "station_name": None}, required=False)
        is None
    )
    assert fake.requests == []


def test_refs_still_rejects_two_identifiers_when_optional(stations):
    with pytest.raises(
        ValueError,
        match="At most one of 'station_id' or 'station_name' can be provided.",
    ):
        stations.refs({"station_id": "95_2", "station_name": "Lagga_2"}, required=False)


def test_ref_passes_a_station_id_through_without_a_request(fake, stations):
    assert stations.ref({"station_id": "95_2", "station_name": None}) == "95_2"
    assert fake.requests == []


def test_ref_looks_up_the_station_id_of_a_station_name(fake, stations, caplog):
    fake.add("", stations_response(("95_2", "Lagga_2")))

    assert stations.ref({"station_id": None, "station_name": "Lagga_2"}) == "95_2"
    assert "additional API request" in caplog.text


def test_ref_raises_ambiguous_when_several_stations_share_the_name(fake, stations):
    fake.add("", stations_response(("95_2", "Lagga"), ("95_3", "Lagga")))

    with pytest.raises(SGUAmbiguousError, match="Multiple stations found"):
        stations.ref({"station_id": None, "station_name": "Lagga"})
