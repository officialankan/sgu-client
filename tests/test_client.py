"""Basic tests for SGU Client."""

import pytest

from sgu_client import SGUAPIError, SGUClient, SGUConfig


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


def test_request_with_kwargs() -> None:
    """Test that we can pass additional kwargs to the request method."""
    client = SGUClient(config=SGUConfig(debug=True))
    _ = client.levels.observed.get_stations(
        limit=1, params={"key": "value"}, data={"key": "value"}
    )


def test_http_error() -> None:
    client = SGUClient(
        config=SGUConfig(debug=True, base_url="https://httpbin.org/status/404")
    )
    with pytest.raises(SGUAPIError):
        _ = client.levels.observed.get_stations(limit=1)
