"""Basic tests for observed groundwater levels endpoints."""

from datetime import UTC, datetime

import pytest

from sgu_client import SGUClient
from sgu_client.models.observed import (
    GroundwaterMeasurement,
    GroundwaterMeasurementCollection,
    GroundwaterStation,
)

TEST_STATION_ID = "stationer.4086"
TEST_STATION_PLATSBETECKNING = "95_2"
TEST_STATION_OBSPLATSNAMN = "Lagga_2"
TEST_MEASUREMENT_ID = "nivaer.1"
TEST_MEASUREMENT_METOD_FOR_M = "klucklod"
TEST_STATIONS_FILTER = "platsbeteckning in ('95_2', '101_1')"


def test_create_basic_client() -> None:
    client = SGUClient()
    assert hasattr(client, "levels")
    assert hasattr(client.levels, "observed")


def test_get_lagga_station_by_id() -> None:
    client = SGUClient()
    station = client.levels.observed.get_station(TEST_STATION_ID)
    assert station is not None
    assert isinstance(station, GroundwaterStation)
    assert station.id == TEST_STATION_ID
    assert station.properties.platsbeteckning == TEST_STATION_PLATSBETECKNING
    assert station.properties.obsplatsnamn == TEST_STATION_OBSPLATSNAMN


def test_get_measurement_by_id() -> None:
    client = SGUClient()
    measurement = client.levels.observed.get_measurement(TEST_MEASUREMENT_ID)
    assert isinstance(measurement, GroundwaterMeasurement)
    assert measurement.id == TEST_MEASUREMENT_ID
    assert measurement.properties.metod_for_matning == TEST_MEASUREMENT_METOD_FOR_M
    assert isinstance(measurement.properties.observation_date, datetime)


def test_stations_to_dataframe() -> None:
    client = SGUClient()
    stations = client.levels.observed.get_stations(filter_expr=TEST_STATIONS_FILTER)
    assert stations is not None
    df = stations.to_dataframe()
    assert not df.empty
    assert "platsbeteckning" in df.columns
    assert "obsplatsnamn" in df.columns
    assert all(
        station in df["platsbeteckning"].tolist() for station in ["95_2", "101_1"]
    )


def test_station_by_name_platsbeteckning() -> None:
    client = SGUClient()
    station = client.levels.observed.get_station_by_name(
        platsbeteckning=TEST_STATION_PLATSBETECKNING
    )
    assert station is not None
    assert isinstance(station, GroundwaterStation)
    assert station.id == TEST_STATION_ID
    assert station.properties.platsbeteckning == TEST_STATION_PLATSBETECKNING
    assert station.properties.obsplatsnamn == TEST_STATION_OBSPLATSNAMN


def test_station_by_name_obsplatsnamn() -> None:
    client = SGUClient()
    station = client.levels.observed.get_station_by_name(
        obsplatsnamn=TEST_STATION_OBSPLATSNAMN
    )
    assert station is not None
    assert isinstance(station, GroundwaterStation)
    assert station.id == TEST_STATION_ID
    assert station.properties.platsbeteckning == TEST_STATION_PLATSBETECKNING
    assert station.properties.obsplatsnamn == TEST_STATION_OBSPLATSNAMN


def test_station_by_name_no_args() -> None:
    client = SGUClient()
    with pytest.raises(
        ValueError, match="Either 'platsbeteckning' or 'obsplatsnamn' must be provided."
    ):
        client.levels.observed.get_station_by_name()


def test_station_by_name_both_args() -> None:
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'platsbeteckning' or 'obsplatsnamn' can be provided.",
    ):
        client.levels.observed.get_station_by_name(
            platsbeteckning=TEST_STATION_PLATSBETECKNING,
            obsplatsnamn=TEST_STATION_OBSPLATSNAMN,
        )


def test_get_stations_by_names_platsbeteckning() -> None:
    client = SGUClient()
    stations = client.levels.observed.get_stations_by_names(
        platsbeteckning=["95_2", "101_1"]
    )
    assert stations is not None
    assert len(stations.features) >= 2
    platsbeteckning = [
        station.properties.platsbeteckning for station in stations.features
    ]
    assert "95_2" in platsbeteckning
    assert "101_1" in platsbeteckning


def test_get_stations_by_names_obsplatsnamn() -> None:
    client = SGUClient()
    stations = client.levels.observed.get_stations_by_names(obsplatsnamn=["Lagga_2"])
    assert stations is not None
    assert len(stations.features) >= 1
    obsplatsnamn_list = [
        station.properties.obsplatsnamn for station in stations.features
    ]
    assert "Lagga_2" in obsplatsnamn_list


def test_get_stations_by_names_single_station() -> None:
    client = SGUClient()
    stations = client.levels.observed.get_stations_by_names(
        platsbeteckning=[TEST_STATION_PLATSBETECKNING]
    )
    assert stations is not None
    assert len(stations.features) == 1
    station = stations.features[0]
    assert station.properties.platsbeteckning == TEST_STATION_PLATSBETECKNING
    assert station.properties.obsplatsnamn == TEST_STATION_OBSPLATSNAMN


def test_get_stations_by_names_no_args() -> None:
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Either 'platsbeteckningar' or 'obsplatsnamn' must be provided.",
    ):
        client.levels.observed.get_stations_by_names()


def test_get_stations_by_names_both_args() -> None:
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'platsbeteckningar' or 'obsplatsnamn' can be provided.",
    ):
        client.levels.observed.get_stations_by_names(
            platsbeteckning=["95_2"], obsplatsnamn=["Lagga_2"]
        )


def test_get_stations_by_names_empty_list() -> None:
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Either 'platsbeteckningar' or 'obsplatsnamn' must be provided.",
    ):
        client.levels.observed.get_stations_by_names(platsbeteckning=[])


def test_get_stations_by_names_to_dataframe() -> None:
    client = SGUClient()
    stations = client.levels.observed.get_stations_by_names(
        platsbeteckning=["95_2", "101_1"]
    )
    assert stations is not None
    df = stations.to_dataframe()
    assert not df.empty
    assert len(df) >= 2
    assert "platsbeteckning" in df.columns
    assert "obsplatsnamn" in df.columns
    assert all(
        station in df["platsbeteckning"].tolist() for station in ["95_2", "101_1"]
    )


# Tests for get_measurements_by_name() function
def test_get_measurements_by_name_platsbeteckning() -> None:
    client = SGUClient()
    measurements = client.levels.observed.get_measurements_by_name(
        platsbeteckning=TEST_STATION_PLATSBETECKNING, limit=10
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    assert len(measurements.features) > 0
    # All measurements should be from the same station
    for measurement in measurements.features:
        assert measurement.properties.platsbeteckning == TEST_STATION_PLATSBETECKNING


def test_get_measurements_by_name_obsplatsnamn() -> None:
    client = SGUClient()
    measurements = client.levels.observed.get_measurements_by_name(
        obsplatsnamn=TEST_STATION_OBSPLATSNAMN, limit=10
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    assert len(measurements.features) > 0
    # All measurements should be from the same station (platsbeteckning)
    for measurement in measurements.features:
        assert measurement.properties.platsbeteckning == TEST_STATION_PLATSBETECKNING


def test_get_measurements_by_name_with_time_filter() -> None:
    client = SGUClient()
    tmin = datetime(2020, 1, 1, tzinfo=UTC)
    tmax = datetime(2021, 1, 1, tzinfo=UTC)
    measurements = client.levels.observed.get_measurements_by_name(
        platsbeteckning=TEST_STATION_PLATSBETECKNING, tmin=tmin, tmax=tmax, limit=10
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    # Check that measurements are within the time range
    for measurement in measurements.features:
        obs_date = measurement.properties.observation_date
        if obs_date:
            assert tmin <= obs_date <= tmax


def test_get_measurements_by_name_with_string_dates() -> None:
    client = SGUClient()
    measurements = client.levels.observed.get_measurements_by_name(
        platsbeteckning=TEST_STATION_PLATSBETECKNING,
        tmin="2020-01-01T00:00:00Z",
        tmax="2021-01-01T00:00:00Z",
        limit=5,
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)


def test_get_measurements_by_name_no_args() -> None:
    client = SGUClient()
    with pytest.raises(
        ValueError, match="Either 'platsbeteckning' or 'obsplatsnamn' must be provided."
    ):
        client.levels.observed.get_measurements_by_name()


def test_get_measurements_by_name_both_args() -> None:
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'platsbeteckning' or 'obsplatsnamn' can be provided.",
    ):
        client.levels.observed.get_measurements_by_name(
            platsbeteckning=TEST_STATION_PLATSBETECKNING,
            obsplatsnamn=TEST_STATION_OBSPLATSNAMN,
        )


# Tests for get_measurements_by_names() function
def test_get_measurements_by_names_platsbeteckning() -> None:
    client = SGUClient()
    measurements = client.levels.observed.get_measurements_by_names(
        platsbeteckning=["95_2", "101_1"], limit=20
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    assert len(measurements.features) > 0
    # Check that we have measurements from the requested stations
    platsbeteckningar = {
        measurement.properties.platsbeteckning for measurement in measurements.features
    }
    assert "95_2" in platsbeteckningar or "101_1" in platsbeteckningar


def test_get_measurements_by_names_obsplatsnamn() -> None:
    client = SGUClient()
    measurements = client.levels.observed.get_measurements_by_names(
        obsplatsnamn=["Lagga_2"], limit=10
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    assert len(measurements.features) > 0
    # All measurements should be from the station with obsplatsnamn "Lagga_2"
    for measurement in measurements.features:
        assert measurement.properties.platsbeteckning == TEST_STATION_PLATSBETECKNING


def test_get_measurements_by_names_with_time_filter() -> None:
    client = SGUClient()
    tmin = datetime(2020, 1, 1, tzinfo=UTC)
    tmax = datetime(2021, 1, 1, tzinfo=UTC)
    measurements = client.levels.observed.get_measurements_by_names(
        platsbeteckning=["95_2"], tmin=tmin, tmax=tmax, limit=10
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    # Check that measurements are within the time range
    for measurement in measurements.features:
        obs_date = measurement.properties.observation_date
        if obs_date:
            assert tmin <= obs_date <= tmax


def test_get_measurements_by_names_no_args() -> None:
    client = SGUClient()
    with pytest.raises(
        ValueError, match="Either 'platsbeteckning' or 'obsplatsnamn' must be provided."
    ):
        client.levels.observed.get_measurements_by_names()


def test_get_measurements_by_names_both_args() -> None:
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'platsbeteckning' or 'obsplatsnamn' can be provided.",
    ):
        client.levels.observed.get_measurements_by_names(
            platsbeteckning=["95_2"], obsplatsnamn=["Lagga_2"]
        )


# Tests for datetime filters helper
def test_build_datetime_filters_helper() -> None:
    client = SGUClient()

    # Test both tmin and tmax
    tmin = datetime(2020, 1, 1, tzinfo=UTC)
    tmax = datetime(2021, 1, 1, tzinfo=UTC)
    filters = client.levels.observed._build_datetime_filters(tmin, tmax)
    expected = [
        "obsdatum >= '2020-01-01T00:00:00+00:00'",
        "obsdatum <= '2021-01-01T00:00:00+00:00'",
    ]
    assert filters == expected

    # Test only tmin
    filters = client.levels.observed._build_datetime_filters(tmin, None)
    expected = ["obsdatum >= '2020-01-01T00:00:00+00:00'"]
    assert filters == expected

    # Test only tmax
    filters = client.levels.observed._build_datetime_filters(None, tmax)
    expected = ["obsdatum <= '2021-01-01T00:00:00+00:00'"]
    assert filters == expected

    # Test string inputs
    filters = client.levels.observed._build_datetime_filters(
        "2020-01-01T00:00:00Z", "2021-01-01T00:00:00Z"
    )
    expected = [
        "obsdatum >= '2020-01-01T00:00:00Z'",
        "obsdatum <= '2021-01-01T00:00:00Z'",
    ]
    assert filters == expected

    # Test no inputs
    filters = client.levels.observed._build_datetime_filters(None, None)
    assert filters == []


def test_measurements_to_dataframe() -> None:
    client = SGUClient()
    measurements = client.levels.observed.get_measurements_by_name(
        platsbeteckning=TEST_STATION_PLATSBETECKNING, limit=5
    )
    assert measurements is not None
    df = measurements.to_dataframe()
    assert not df.empty
    assert "platsbeteckning" in df.columns
    assert "observation_date" in df.columns
    assert "grundvattenniva_m_o_h" in df.columns
    assert all(
        platsbeteckning == TEST_STATION_PLATSBETECKNING
        for platsbeteckning in df["platsbeteckning"].tolist()
    )
