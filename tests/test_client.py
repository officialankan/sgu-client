"""Basic tests for SGU Client using mocked API responses.

These tests use mocked HTTP responses to ensure fast, reliable testing without
depending on external API availability.
"""

from unittest.mock import Mock, patch

import pytest
from requests import Response

from sgu_client import SGUAPIError, SGUClient, SGUConfig
from tests.mock_responses import create_mock_single_station_response


def create_mock_response(response_data, status_code=200):
    """Create a mock HTTP response object."""
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = status_code
    mock_response.json.return_value = response_data
    return mock_response


def test_create_basic_client():
    """Test that we can create a basic SGUClient instance."""
    client = SGUClient()
    assert client is not None


def test_create_client_with_config():
    """Test that we can create a SGUClient with custom configuration."""
    config = SGUConfig(timeout=30, debug=True)
    client = SGUClient(config=config)
    assert client is not None


def test_client_context_manager():
    """Test that SGUClient works as a context manager."""
    with SGUClient() as client:
        assert client is not None


@patch.object(SGUClient().levels.observed._client._session, "request")
def test_request_with_kwargs(mock_request) -> None:
    """Test that we can pass additional kwargs to the request method."""
    mock_response_data = create_mock_single_station_response(
        station_id="stationer.test",
        platsbeteckning="TEST_1",
        obsplatsnamn="Test_Station",
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient(config=SGUConfig(debug=True))
    _ = client.levels.observed.get_stations(
        limit=1, params={"key": "value"}, data={"key": "value"}
    )


def test_http_error() -> None:
    """Test that HTTP errors are properly raised."""
    with patch("requests.Session.request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not Found"}
        mock_request.return_value = mock_response

        client = SGUClient(config=SGUConfig(debug=True))
        with pytest.raises(SGUAPIError):
            _ = client.levels.observed.get_stations(limit=1)
