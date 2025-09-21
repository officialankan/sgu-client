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
    assert station.properties.platsbeteckning == TEST_STATION_PLATSBETECKNING
    assert station.properties.obsplatsnamn == TEST_STATION_OBSPLATSNAMN

    # Verify geometry is present and valid
    assert station.geometry is not None
    assert station.geometry.type == "Point"
    assert len(station.geometry.coordinates) == 2
    assert isinstance(station.geometry.coordinates[0], int | float)
    assert isinstance(station.geometry.coordinates[1], int | float)

    # Verify essential properties are present
    assert station.properties.kommun is not None
    assert station.properties.lan is not None


def test_real_api_integration_get_recent_measurements():
    """INTEGRATION TEST: Verify measurement retrieval still works.

    Tests that we can retrieve recent measurements and that the data structure
    is as expected. Uses a small limit to avoid long test times.
    """
    client = SGUClient()

    # Get recent measurements for our test station (last 2 years)
    tmin = datetime(2022, 1, 1, tzinfo=UTC)
    measurements = client.levels.observed.get_measurements_by_name(
        platsbeteckning=TEST_STATION_PLATSBETECKNING,
        tmin=tmin,
        limit=5,  # Keep small for fast test
    )

    # Basic validation - should have some measurements
    assert measurements is not None
    assert len(measurements.features) > 0

    # Check first measurement structure
    measurement = measurements.features[0]
    assert measurement.properties.platsbeteckning == TEST_STATION_PLATSBETECKNING
    assert measurement.properties.observation_date is not None
    assert isinstance(measurement.properties.observation_date, datetime)
    assert measurement.properties.grundvattenniva_m_o_h is not None
    assert isinstance(measurement.properties.grundvattenniva_m_o_h, int | float)
