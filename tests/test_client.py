"""Basic tests for SGU Client."""

from sgu_client import SGUClient, SGUConfig


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
