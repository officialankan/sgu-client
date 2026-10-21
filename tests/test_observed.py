"""Tests for observed groundwater levels endpoints using mocked API responses.

These tests use mocked HTTP responses to ensure fast, reliable testing without
depending on external API availability. For integration tests that verify the
real API still works, see test_actual_api.py.
"""

from datetime import UTC, datetime

import pytest
from pandas.api.types import is_datetime64_any_dtype as is_datetime

from sgu_client import SGUClient, TransportResponse
from sgu_client.exceptions import (
    SGUAPIError,
    SGUConnectionError,
    SGUNotFoundError,
    SGUTimeoutError,
)
from sgu_client.models.observed import (
    GroundwaterMeasurement,
    GroundwaterMeasurementCollection,
    GroundwaterStation,
)
from tests.mock_responses import (
    create_mock_empty_collection_response,
    create_mock_multiple_measurements_response,
    create_mock_multiple_stations_response,
    create_mock_single_measurement_response,
    create_mock_single_station_response,
    create_mock_station_collection_response,
    create_mock_station_feature,
)

# Test constants
TEST_STATION_ID = "stationer.4086"
TEST_STATION_PLATSBETECKNING = "95_2"
TEST_STATION_OBSPLATSNAMN = "Lagga_2"
TEST_MEASUREMENT_ID = "nivaer.1"
TEST_MEASUREMENT_METOD_FOR_M = "klucklod"
TEST_STATIONS_FILTER = "platsbeteckning in ('95_2', '101_1')"


def test_create_basic_client() -> None:
    """Test that basic client creation works."""
    client = SGUClient()
    assert hasattr(client, "levels")
    assert hasattr(client.levels, "observed")


def test_get_lagga_station_by_id(fake, client) -> None:
    """Test getting a specific station by ID with mocked response."""
    mock_response_data = create_mock_single_station_response(
        station_id=TEST_STATION_ID,
        platsbeteckning=TEST_STATION_PLATSBETECKNING,
        obsplatsnamn=TEST_STATION_OBSPLATSNAMN,
    )
    fake.add("", mock_response_data)

    station = client.levels.observed.get_station(TEST_STATION_ID)

    assert station is not None
    assert isinstance(station, GroundwaterStation)
    assert station.id == TEST_STATION_ID
    assert station.properties.station_id == TEST_STATION_PLATSBETECKNING
    assert station.properties.station_name == TEST_STATION_OBSPLATSNAMN


def test_get_measurement_by_id(fake, client) -> None:
    """Test getting a specific measurement by ID with mocked response."""
    mock_response_data = create_mock_single_measurement_response(
        measurement_id=TEST_MEASUREMENT_ID,
        platsbeteckning=TEST_STATION_PLATSBETECKNING,
        metod=TEST_MEASUREMENT_METOD_FOR_M,
    )
    fake.add("", mock_response_data)

    measurement = client.levels.observed.get_measurement(TEST_MEASUREMENT_ID)

    assert isinstance(measurement, GroundwaterMeasurement)
    assert measurement.id == TEST_MEASUREMENT_ID
    assert measurement.properties.measurement_method == TEST_MEASUREMENT_METOD_FOR_M
    assert isinstance(measurement.properties.observation_date, datetime)


def test_stations_to_dataframe(fake, client) -> None:
    """Test converting stations collection to DataFrame with mocked response."""
    mock_response_data = create_mock_multiple_stations_response(
        platsbeteckningar=["95_2", "101_1"], limit=10
    )
    fake.add("", mock_response_data)

    stations = client.levels.observed.get_stations(
        filter_expr=TEST_STATIONS_FILTER, limit=10
    )
    assert stations is not None
    df = stations.to_dataframe()
    assert not df.empty
    assert "station_id" in df.columns
    assert "station_name" in df.columns
    assert all(station in df["station_id"].tolist() for station in ["95_2", "101_1"])


def test_station_by_name_station_id(fake, client) -> None:
    """Test getting station by station_id with mocked response."""
    mock_response_data = create_mock_multiple_stations_response(
        platsbeteckningar=[TEST_STATION_PLATSBETECKNING], limit=1
    )
    fake.add("", mock_response_data)

    station = client.levels.observed.get_station_by_name(
        station_id=TEST_STATION_PLATSBETECKNING
    )
    assert station is not None
    assert isinstance(station, GroundwaterStation)
    assert station.properties.station_id == TEST_STATION_PLATSBETECKNING


def test_station_by_name_station_name(fake, client) -> None:
    """Test getting station by station_name with mocked response."""
    mock_response_data = create_mock_multiple_stations_response(
        platsbeteckningar=[TEST_STATION_PLATSBETECKNING], limit=1
    )
    # Update the obsplatsnamn in the mock response
    mock_response_data["features"][0]["properties"]["obsplatsnamn"] = (
        TEST_STATION_OBSPLATSNAMN
    )
    fake.add("", mock_response_data)

    station = client.levels.observed.get_station_by_name(
        station_name=TEST_STATION_OBSPLATSNAMN
    )
    assert station is not None
    assert isinstance(station, GroundwaterStation)
    assert station.properties.station_id == TEST_STATION_PLATSBETECKNING
    assert station.properties.station_name == TEST_STATION_OBSPLATSNAMN


def test_station_by_name_no_args() -> None:
    """Test that get_station_by_name raises error when no arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError, match="Either 'station_id' or 'station_name' must be provided."
    ):
        client.levels.observed.get_station_by_name()


def test_station_by_name_both_args() -> None:
    """Test that get_station_by_name raises error when both arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'station_id' or 'station_name' can be provided.",
    ):
        client.levels.observed.get_station_by_name(
            station_id=TEST_STATION_PLATSBETECKNING,
            station_name=TEST_STATION_OBSPLATSNAMN,
        )


def test_get_stations_by_names_station_id(fake, client) -> None:
    """Test getting multiple stations by station_id with mocked response."""
    mock_response_data = create_mock_multiple_stations_response(
        platsbeteckningar=["95_2", "101_1"], limit=10
    )
    fake.add("", mock_response_data)

    stations = client.levels.observed.get_stations_by_names(
        station_id=["95_2", "101_1"], limit=10
    )
    assert stations is not None
    assert len(stations.features) >= 2
    platsbeteckning = [station.properties.station_id for station in stations.features]
    assert "95_2" in platsbeteckning
    assert "101_1" in platsbeteckning


def test_get_stations_by_names_station_name(fake, client) -> None:
    """Test getting multiple stations by station_name with mocked response."""
    mock_response_data = create_mock_multiple_stations_response(
        platsbeteckningar=[TEST_STATION_PLATSBETECKNING], limit=5
    )
    # Update obsplatsnamn in mock response
    mock_response_data["features"][0]["properties"]["obsplatsnamn"] = "Lagga_2"
    fake.add("", mock_response_data)

    stations = client.levels.observed.get_stations_by_names(
        station_name=["Lagga_2"], limit=5
    )
    assert stations is not None
    assert len(stations.features) >= 1
    obsplatsnamn_list = [
        station.properties.station_name for station in stations.features
    ]
    assert "Lagga_2" in obsplatsnamn_list


def test_get_stations_by_names_single_station(fake, client) -> None:
    """Test getting single station by platsbeteckning list with mocked response."""
    mock_response_data = create_mock_multiple_stations_response(
        platsbeteckningar=[TEST_STATION_PLATSBETECKNING], limit=5
    )
    # Update obsplatsnamn to match expected value
    mock_response_data["features"][0]["properties"]["obsplatsnamn"] = (
        TEST_STATION_OBSPLATSNAMN
    )
    fake.add("", mock_response_data)

    stations = client.levels.observed.get_stations_by_names(
        station_id=[TEST_STATION_PLATSBETECKNING], limit=5
    )
    assert stations is not None
    assert len(stations.features) == 1
    station = stations.features[0]
    assert station.properties.station_id == TEST_STATION_PLATSBETECKNING
    assert station.properties.station_name == TEST_STATION_OBSPLATSNAMN


def test_get_stations_by_names_no_args() -> None:
    """Test that get_stations_by_names raises error when no arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Either 'station_id' or 'station_name' must be provided.",
    ):
        client.levels.observed.get_stations_by_names()


def test_get_stations_by_names_both_args() -> None:
    """Test that get_stations_by_names raises error when both arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'station_id' or 'station_name' can be provided.",
    ):
        client.levels.observed.get_stations_by_names(
            station_id=["95_2"], station_name=["Lagga_2"]
        )


def test_get_stations_by_names_empty_list() -> None:
    """Test that get_stations_by_names raises error when empty list provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Either 'station_id' or 'station_name' must be provided.",
    ):
        client.levels.observed.get_stations_by_names(station_id=[])


def test_get_stations_by_names_to_dataframe(fake, client) -> None:
    """Test converting multiple stations to DataFrame with mocked response."""
    mock_response_data = create_mock_multiple_stations_response(
        platsbeteckningar=["95_2", "101_1"], limit=10
    )
    fake.add("", mock_response_data)

    stations = client.levels.observed.get_stations_by_names(
        station_id=["95_2", "101_1"], limit=10
    )
    assert stations is not None
    df = stations.to_dataframe()
    assert not df.empty
    assert len(df) >= 2
    assert "station_id" in df.columns
    assert "station_name" in df.columns
    assert all(station in df["station_id"].tolist() for station in ["95_2", "101_1"])


# Tests for get_measurements_by_name() function
def test_get_measurements_by_name_station_id(fake, client) -> None:
    """Test getting measurements by station_id with mocked response."""
    mock_response_data = create_mock_multiple_measurements_response(
        platsbeteckning=TEST_STATION_PLATSBETECKNING, count=5
    )
    fake.add("", mock_response_data)

    measurements = client.levels.observed.get_measurements_by_name(
        station_id=TEST_STATION_PLATSBETECKNING, limit=10
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    assert len(measurements.features) > 0
    # All measurements should be from the same station
    for measurement in measurements.features:
        assert measurement.properties.station_id == TEST_STATION_PLATSBETECKNING


def test_get_measurements_by_name_station_name(fake, client) -> None:
    """Test getting measurements by station_name with mocked response."""
    # station_name lookup resolves the station first, then fetches measurements
    fake.add(
        "",
        create_mock_single_station_response(),
        create_mock_multiple_measurements_response(
            platsbeteckning=TEST_STATION_PLATSBETECKNING, count=5
        ),
    )

    measurements = client.levels.observed.get_measurements_by_name(
        station_name=TEST_STATION_OBSPLATSNAMN, limit=10
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    assert len(measurements.features) > 0
    # All measurements should be from the same station (platsbeteckning)
    for measurement in measurements.features:
        assert measurement.properties.station_id == TEST_STATION_PLATSBETECKNING


def test_get_measurements_by_name_with_time_filter(fake, client) -> None:
    """Test getting measurements with time filter using mocked response."""
    tmin = datetime(2020, 1, 1, tzinfo=UTC)
    tmax = datetime(2021, 1, 1, tzinfo=UTC)

    # Create measurements within the time range
    mock_response_data = create_mock_multiple_measurements_response(
        platsbeteckning=TEST_STATION_PLATSBETECKNING,
        count=3,
        start_date=datetime(2020, 6, 1, tzinfo=UTC),
    )
    fake.add("", mock_response_data)

    measurements = client.levels.observed.get_measurements_by_name(
        station_id=TEST_STATION_PLATSBETECKNING, tmin=tmin, tmax=tmax, limit=10
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    # Check that measurements are within the time range
    for measurement in measurements.features:
        obs_date = measurement.properties.observation_date
        if obs_date:
            assert tmin <= obs_date <= tmax


def test_get_measurements_by_name_with_string_dates(fake, client) -> None:
    """Test getting measurements with string date filters using mocked response."""
    mock_response_data = create_mock_multiple_measurements_response(
        platsbeteckning=TEST_STATION_PLATSBETECKNING,
        count=3,
        start_date=datetime(2020, 6, 1, tzinfo=UTC),
    )
    fake.add("", mock_response_data)

    measurements = client.levels.observed.get_measurements_by_name(
        station_id=TEST_STATION_PLATSBETECKNING,
        tmin="2020-01-01T00:00:00Z",
        tmax="2021-01-01T00:00:00Z",
        limit=5,
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)


def test_get_measurements_by_name_no_args() -> None:
    """Test that get_measurements_by_name raises error when no arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError, match="Either 'station_id' or 'station_name' must be provided."
    ):
        client.levels.observed.get_measurements_by_name()


def test_get_measurements_by_name_both_args(client) -> None:
    """Test that get_measurements_by_name raises error when both arguments provided."""
    with pytest.raises(
        ValueError,
        match="Only one of 'station_id' or 'station_name' can be provided.",
    ):
        client.levels.observed.get_measurements_by_name(
            station_id=TEST_STATION_PLATSBETECKNING,
            station_name=TEST_STATION_OBSPLATSNAMN,
        )


# Tests for get_measurements_by_names() function
def test_get_measurements_by_names_station_id(fake, client) -> None:
    """Test getting measurements for multiple stations with mocked response."""
    # Create measurements for both stations
    measurements_95_2 = create_mock_multiple_measurements_response(
        platsbeteckning="95_2", count=3
    )["features"]
    measurements_101_1 = create_mock_multiple_measurements_response(
        platsbeteckning="101_1", count=2
    )["features"]

    # Update platsbeteckning for second set
    for m in measurements_101_1:
        m["properties"]["platsbeteckning"] = "101_1"

    all_measurements = measurements_95_2 + measurements_101_1
    mock_response_data = create_mock_multiple_measurements_response(count=0)
    mock_response_data["features"] = all_measurements
    mock_response_data["numberReturned"] = len(all_measurements)
    fake.add("", mock_response_data)

    measurements = client.levels.observed.get_measurements_by_names(
        station_id=["95_2", "101_1"], limit=20
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    assert len(measurements.features) > 0
    # Check that we have measurements from the requested stations
    station_ids = {
        measurement.properties.station_id for measurement in measurements.features
    }
    assert "95_2" in station_ids or "101_1" in station_ids


def test_get_measurements_by_names_station_name(fake, client) -> None:
    """Test getting measurements by station_name with mocked response."""
    # station_name lookup resolves the stations first, then fetches measurements
    fake.add("stationer/items", create_mock_single_station_response())
    fake.add(
        "nivaer/items",
        create_mock_multiple_measurements_response(
            platsbeteckning=TEST_STATION_PLATSBETECKNING, count=5
        ),
    )

    measurements = client.levels.observed.get_measurements_by_names(
        station_name=["Lagga_2"], limit=10
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    assert len(measurements.features) > 0
    # All measurements should be from the station with obsplatsnamn "Lagga_2"
    for measurement in measurements.features:
        assert measurement.properties.station_id == TEST_STATION_PLATSBETECKNING


def test_get_measurements_by_names_with_time_filter(fake, client) -> None:
    """Test getting measurements for multiple stations with time filter using mocked response."""
    tmin = datetime(2020, 1, 1, tzinfo=UTC)
    tmax = datetime(2021, 1, 1, tzinfo=UTC)

    mock_response_data = create_mock_multiple_measurements_response(
        platsbeteckning="95_2", count=3, start_date=datetime(2020, 6, 1, tzinfo=UTC)
    )
    fake.add("", mock_response_data)

    measurements = client.levels.observed.get_measurements_by_names(
        station_id=["95_2"], tmin=tmin, tmax=tmax, limit=10
    )
    assert measurements is not None
    assert isinstance(measurements, GroundwaterMeasurementCollection)
    # Check that measurements are within the time range
    for measurement in measurements.features:
        obs_date = measurement.properties.observation_date
        if obs_date:
            assert tmin <= obs_date <= tmax


def test_get_measurements_by_names_no_args() -> None:
    """Test that get_measurements_by_names raises error when no arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError, match="Either 'station_id' or 'station_name' must be provided."
    ):
        client.levels.observed.get_measurements_by_names()


def test_get_measurements_by_names_both_args() -> None:
    """Test that get_measurements_by_names raises error when both arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'station_id' or 'station_name' can be provided.",
    ):
        client.levels.observed.get_measurements_by_names(
            station_id=["95_2"], station_name=["Lagga_2"]
        )


def test_measurements_to_dataframe(fake, client) -> None:
    """Test converting measurements to DataFrame with mocked response."""
    mock_response_data = create_mock_multiple_measurements_response(
        platsbeteckning=TEST_STATION_PLATSBETECKNING, count=5
    )
    fake.add("", mock_response_data)

    measurements = client.levels.observed.get_measurements_by_name(
        station_id=TEST_STATION_PLATSBETECKNING, limit=5
    )
    assert measurements is not None
    df = measurements.to_dataframe()
    assert not df.empty
    assert "station_id" in df.columns
    assert "observation_date" in df.columns
    assert "water_level_masl_m" in df.columns
    assert all(
        station_id == TEST_STATION_PLATSBETECKNING
        for station_id in df["station_id"].tolist()
    )

    # Assert that it is sorted by 'observation_date'
    assert is_datetime(df["observation_date"])
    assert df["observation_date"].is_monotonic_increasing


def test_measurements_to_series(fake, client) -> None:
    """Test converting measurements to pandas Series with mocked response."""
    mock_response_data = create_mock_multiple_measurements_response(
        platsbeteckning=TEST_STATION_PLATSBETECKNING, count=5
    )
    fake.add("", mock_response_data)

    measurements = client.levels.observed.get_measurements_by_name(
        station_id=TEST_STATION_PLATSBETECKNING, limit=5
    )
    assert measurements is not None
    series = measurements.to_series()
    assert not series.empty
    assert series.name == "water_level_masl_m"
    assert is_datetime(series.index)


def test_measurements_to_series_custom_index_data(fake, client) -> None:
    """Test converting measurements to Series with custom index/data columns using mocked response."""
    mock_response_data = create_mock_multiple_measurements_response(
        platsbeteckning=TEST_STATION_PLATSBETECKNING, count=5
    )
    fake.add("", mock_response_data)

    measurements = client.levels.observed.get_measurements_by_name(
        station_id=TEST_STATION_PLATSBETECKNING, limit=5
    )
    assert measurements is not None
    series = measurements.to_series(
        index="observation_date", data="water_level_below_ground_m"
    )
    assert not series.empty
    assert series.name == "water_level_below_ground_m"

    with pytest.raises(ValueError):
        measurements.to_series(index="invalid_column", data="water_level_masl_m")

    with pytest.raises(ValueError):
        measurements.to_series(index="observation_date", data="invalid_column")


# Comprehensive error condition tests (enabled by mocking)
def test_api_timeout_error(fake, client) -> None:
    """Test that API timeout errors are properly raised."""
    fake.add("", SGUTimeoutError("Read timeout"))

    with pytest.raises(SGUTimeoutError, match="Read timeout"):
        client.levels.observed.get_station(TEST_STATION_ID)


def test_api_connection_error(fake, client) -> None:
    """Test that API connection errors are properly raised."""
    fake.add("", SGUConnectionError("Connection failed"))

    with pytest.raises(SGUConnectionError, match="Connection failed"):
        client.levels.observed.get_station(TEST_STATION_ID)


def test_api_server_error(fake, client) -> None:
    """Test that API server errors are properly raised."""
    fake.add("", TransportResponse(500, '{"error": "Internal Server Error"}'))

    with pytest.raises(SGUAPIError, match="API request failed with status 500"):
        client.levels.observed.get_station(TEST_STATION_ID)


def test_api_not_found_error(fake, client) -> None:
    """Test that API 404 errors are properly raised."""
    fake.add("", TransportResponse(404, '{"error": "Station not found"}'))

    with pytest.raises(SGUAPIError, match="API request failed with status 404"):
        client.levels.observed.get_station("nonexistent.station")


def test_empty_station_response_handling(fake, client) -> None:
    """Test handling of empty station responses."""
    mock_response_data = create_mock_empty_collection_response()
    fake.add("", mock_response_data)

    with pytest.raises(ValueError, match="Station .* not found"):
        client.levels.observed.get_station("nonexistent.station")


def test_multiple_station_response_handling(fake, client) -> None:
    """Test handling of multiple stations returned for single ID (edge case)."""
    # Create response with multiple stations (should not happen but test edge case)
    stations = [
        create_mock_station_feature(station_id="duplicate.1"),
        create_mock_station_feature(station_id="duplicate.2"),
    ]
    mock_response_data = create_mock_station_collection_response(stations)
    fake.add("", mock_response_data)

    with pytest.raises(ValueError, match="Multiple stations returned for ID"):
        client.levels.observed.get_station("duplicate.station")


def test_malformed_json_response(fake, client) -> None:
    """Test handling of malformed JSON responses."""
    fake.add("", TransportResponse(500, "Internal Server Error - HTML response"))

    with pytest.raises(SGUAPIError) as exc_info:
        client.levels.observed.get_station(TEST_STATION_ID)

    # Should raise SGUAPIError when JSON parsing fails
    assert "API request failed with status 500" in str(exc_info.value)


def test_station_with_float_idiam(fake, client) -> None:
    """Test that stations with float idiam values are handled correctly.

    This addresses the bug where idiam field was expected to be int but
    the API returns float values like 50.8, causing ValidationError.
    """
    # Create a mock station with float idiam value
    station_data = create_mock_station_feature(
        station_id="stationer.float_idiam", platsbeteckning="float_test"
    )

    # Add the problematic float idiam field to properties
    station_data["properties"]["idiam"] = 50.8
    station_data["properties"]["stationsanmarkning"] = "markanvändningspåverkad"

    collection_data = create_mock_station_collection_response([station_data])

    fake.add("", collection_data)

    # This should not raise a ValidationError anymore
    stations = client.levels.observed.get_stations(
        filter_expr="stationsanmarkning='markanvändningspåverkad'"
    )

    assert len(stations.features) == 1
    station = stations.features[0]

    # Verify the float idiam value is preserved correctly
    assert station.properties.inner_diameter == 50.8
    assert isinstance(station.properties.inner_diameter, float)
    assert station.properties.station_remark == "markanvändningspåverkad"


def test_get_measurement_by_id_not_found(fake, client):
    """Test that get_measurement returns ValueError when measurement not found."""
    # Mock empty response (no features found)
    fake.add("", create_mock_empty_collection_response())

    with pytest.raises(ValueError) as exc_info:
        client.levels.observed.get_measurement("nonexistent_id")

    assert "not found" in str(exc_info.value).lower()


def test_get_measurement_by_id_multiple_results(fake, client):
    """Test that get_measurement returns ValueError when multiple measurements found."""
    # Mock response with multiple measurements (should never happen in practice)
    fake.add(
        "",
        create_mock_multiple_measurements_response(
            count=2  # No start_id parameter
        ),
    )

    with pytest.raises(ValueError) as exc_info:
        client.levels.observed.get_measurement("duplicate_id")

    assert "multiple" in str(exc_info.value).lower()


def test_get_station_by_name_multiple_results(fake, client):
    """Test that get_station_by_name returns ValueError when multiple stations found."""
    # Mock response with multiple stations having the same obsplatsnamn
    fake.add(
        "",
        create_mock_multiple_stations_response(
            platsbeteckningar=["Station1", "Station2"]
        ),
    )

    with pytest.raises(ValueError) as exc_info:
        client.levels.observed.get_station_by_name(station_name="DuplicateName")

    assert "multiple" in str(exc_info.value).lower()


def test_get_stations_parses_active_dates(fake, client) -> None:
    """Station dates come back as UTC datetimes; a live station has no end date."""
    fake.add(
        "",
        create_mock_station_collection_response(
            stations=[
                create_mock_station_feature(fdat="1996-04-29Z", tdat="2018-12-10Z"),
                create_mock_station_feature(station_id="stationer.1", tdat=None),
            ]
        ),
    )

    stations = client.levels.observed.get_stations(limit=10)

    closed, live = (station.properties for station in stations.features)
    assert closed.active_since == datetime(1996, 4, 29, tzinfo=UTC)
    assert closed.active_until == datetime(2018, 12, 10, tzinfo=UTC)
    assert live.active_until is None


def test_get_station_by_name_not_found(fake, client):
    """Test that get_station_by_name raises SGUNotFoundError when nothing matches."""
    fake.add("", create_mock_empty_collection_response())

    with pytest.raises(SGUNotFoundError, match="No stations found for"):
        client.levels.observed.get_station_by_name(station_name="Nope")


def test_get_measurements_filters_on_observation_date(fake, client) -> None:
    fake.add("", create_mock_empty_collection_response())
    client.levels.observed.get_measurements(
        tmin=datetime(2020, 1, 1, tzinfo=UTC), tmax="2021-01-01"
    )

    assert fake.params["filter"] == (
        "obsdatum >= '2020-01-01T00:00:00+00:00' AND obsdatum <= '2021-01-01'"
    )
