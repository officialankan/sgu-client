"""Integration tests that make actual API calls to verify the real SGU API still works.

These tests serve as canary tests to detect when the SGU API changes in ways that
would break our client. They should be kept minimal to avoid long test runs and
API rate limiting, but comprehensive enough to catch breaking changes.
"""

from datetime import UTC, datetime

from sgu_client import SGUClient
from sgu_client.models.observed import GroundwaterStation

# Test constants - same as in test_observed.py
TEST_STATION_ID = "stationer.4086"
TEST_STATION_PLATSBETECKNING = "95_2"
TEST_STATION_OBSPLATSNAMN = "Lagga_2"


def test_real_api_integration_get_lagga_station():
    """INTEGRATION TEST: Verify real SGU API still works as expected.

    This is our canary test to detect API changes. It tests the core functionality
    of retrieving a specific groundwater station by ID and validates that:
    1. The API still responds correctly
    2. The response structure hasn't changed
    3. Our data models still parse correctly
    4. The expected test station still exists with expected properties
    """
    client = SGUClient()
    station = client.levels.observed.get_station(TEST_STATION_ID)

    # Basic assertions to verify API contract
    assert station is not None
    assert isinstance(station, GroundwaterStation)
    assert station.id == TEST_STATION_ID
    assert station.properties.station_id == TEST_STATION_PLATSBETECKNING
    assert station.properties.station_name == TEST_STATION_OBSPLATSNAMN

    # Verify geometry is present and valid
    assert station.geometry is not None
    assert station.geometry.type == "Point"
    assert len(station.geometry.coordinates) == 2
    assert isinstance(station.geometry.coordinates[0], int | float)
    assert isinstance(station.geometry.coordinates[1], int | float)

    # Verify essential properties are present
    assert station.properties.municipality is not None
    assert station.properties.county is not None


def test_real_api_integration_get_recent_measurements():
    """INTEGRATION TEST: Verify measurement retrieval still works.

    Tests that we can retrieve recent measurements and that the data structure
    is as expected. Uses a small limit to avoid long test times.
    """
    client = SGUClient()

    # Get recent measurements for our test station (last 2 years)
    tmin = datetime(2022, 1, 1, tzinfo=UTC)
    measurements = client.levels.observed.get_measurements_by_name(
        station_id=TEST_STATION_PLATSBETECKNING,
        tmin=tmin,
        limit=5,  # Keep small for fast test
    )

    # Basic validation - should have some measurements
    assert measurements is not None
    assert len(measurements.features) > 0

    # Check first measurement structure
    measurement = measurements.features[0]
    assert measurement.properties.station_id == TEST_STATION_PLATSBETECKNING
    assert measurement.properties.observation_date is not None
    assert isinstance(measurement.properties.observation_datetime, datetime)
    assert measurement.properties.water_level_masl_m is not None
    assert isinstance(measurement.properties.water_level_masl_m, int | float)


def test_real_api_chemistry_sampling_sites():
    """INTEGRATION TEST: Verify chemistry API sampling sites endpoint works.

    This canary test ensures the chemistry API is accessible and returns
    expected data structures.
    """
    client = SGUClient()

    # Get a small number of sampling sites
    sites = client.chemistry.get_sampling_sites(limit=5)

    # Basic validation
    assert sites is not None
    assert len(sites.features) > 0
    assert sites.numberReturned is not None

    # Check first site structure
    site = sites.features[0]
    assert site.properties.station_id is not None
    assert site.properties.national_site_id is not None
    assert site.properties.municipality is not None


def test_real_api_chemistry_analysis_results():
    """INTEGRATION TEST: Verify chemistry API analysis results endpoint works.

    Tests that we can retrieve chemical analysis results with expected structure.
    """
    client = SGUClient()

    # Get a small number of analysis results
    results = client.chemistry.get_analysis_results(limit=5)

    # Basic validation
    assert results is not None
    assert len(results.features) > 0

    # Check first result structure
    result = results.features[0]
    assert result.properties.station_id is not None
    assert result.properties.parameter_name is not None
    assert result.properties.parameter_short_name is not None
    # measurement_value can be None for some results
    assert result.properties.sampling_date is not None
    assert isinstance(result.properties.sampling_datetime, datetime)
