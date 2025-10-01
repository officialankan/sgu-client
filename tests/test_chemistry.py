"""Tests for chemistry module with mocked API responses."""

from unittest.mock import Mock, patch

from requests import Response

from sgu_client import SGUClient
from sgu_client.models.chemistry import (
    AnalysisResult,
    AnalysisResultCollection,
    SamplingSite,
    SamplingSiteCollection,
)
from tests.mock_responses import (
    create_mock_multiple_analysis_results_response,
    create_mock_single_sampling_site_response,
)


def create_mock_response(response_data, status_code=200):
    """Create a mock HTTP response object."""
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = status_code
    mock_response.json.return_value = response_data
    return mock_response


def test_chemistry_client_exists():
    """Test that chemistry client is accessible."""
    client = SGUClient()
    assert hasattr(client, "chemistry")
    assert hasattr(client.chemistry, "get_sampling_sites")
    assert hasattr(client.chemistry, "get_analysis_results")


def test_chemistry_models_importable():
    """Test that chemistry models can be imported."""
    assert AnalysisResult is not None
    assert AnalysisResultCollection is not None
    assert SamplingSite is not None
    assert SamplingSiteCollection is not None


def test_get_sampling_sites_with_mock():
    """Test getting sampling sites with mocked response."""
    client = SGUClient()

    # Create mock response for a single sampling site
    mock_response_data = create_mock_single_sampling_site_response(
        site_id="provplatser.3",
        platsbeteckning="10001_1",
        provplatsnamn="Test_Site",
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the method
        sites = client.chemistry.get_sampling_sites(limit=1)

        # Verify results
        assert sites is not None
        assert isinstance(sites, SamplingSiteCollection)
        assert len(sites.features) == 1
        assert sites.features[0].properties.station_id == "10001_1"
        assert sites.features[0].properties.site_name == "Test_Site"


def test_get_analysis_results_with_mock():
    """Test getting analysis results with mocked response."""
    client = SGUClient()

    # Create mock response for analysis results
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[("pH", "PH", 7.2)],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the method
        results = client.chemistry.get_analysis_results(limit=1)

        # Verify results
        assert results is not None
        assert isinstance(results, AnalysisResultCollection)
        assert len(results.features) == 1
        assert results.features[0].properties.station_id == "10001_1"
        assert results.features[0].properties.parameter_short_name == "PH"
        assert results.features[0].properties.measurement_value == 7.2


def test_get_sampling_site_by_name_station_id():
    """Test getting a single sampling site by station_id with mocked response."""
    client = SGUClient()

    # Create mock response with one site matching the station_id
    mock_response_data = create_mock_single_sampling_site_response(
        site_id="provplatser.3",
        platsbeteckning="10001_1",
        provplatsnamn="Test_Site",
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the convenience method
        site = client.chemistry.get_sampling_site_by_name(station_id="10001_1")

        # Verify results
        assert site is not None
        assert isinstance(site, SamplingSite)
        assert site.properties.station_id == "10001_1"
        assert site.properties.site_name == "Test_Site"


def test_get_sampling_site_by_name_site_name():
    """Test getting a single sampling site by site_name with mocked response."""
    client = SGUClient()

    # Create mock response with one site matching the site_name
    mock_response_data = create_mock_single_sampling_site_response(
        site_id="provplatser.3",
        platsbeteckning="10001_1",
        provplatsnamn="Test_Site",
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the convenience method using site_name
        site = client.chemistry.get_sampling_site_by_name(site_name="Test_Site")

        # Verify results
        assert site is not None
        assert isinstance(site, SamplingSite)
        assert site.properties.station_id == "10001_1"
        assert site.properties.site_name == "Test_Site"


def test_get_sampling_sites_by_names():
    """Test getting multiple sampling sites by names with mocked response."""
    from tests.mock_responses import create_mock_multiple_sampling_sites_response

    client = SGUClient()

    # Create mock response with multiple sites
    mock_response_data = create_mock_multiple_sampling_sites_response(
        platsbeteckningar=["10001_1", "10002_1"],
        limit=10,
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the convenience method for multiple sites
        sites = client.chemistry.get_sampling_sites_by_names(
            station_id=["10001_1", "10002_1"]
        )

        # Verify results
        assert sites is not None
        assert isinstance(sites, SamplingSiteCollection)
        assert len(sites.features) == 2
        assert sites.features[0].properties.station_id == "10001_1"
        assert sites.features[1].properties.station_id == "10002_1"
