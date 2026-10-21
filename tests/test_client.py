"""Tests for creating, configuring and closing an SGUClient."""

from unittest.mock import patch

from sgu_client import (
    RequestsTransport,
    SGUClient,
    SGUConfig,
)
from tests.fakes import FakeTransport, Request
from tests.mock_responses import create_mock_single_station_response

OBSERVED_URL = (
    "https://api.sgu.se/oppnadata/grundvattennivaer-observerade/ogc/features/v1/"
)


def test_create_basic_client():
    """Test that we can create a basic SGUClient instance."""
    client = SGUClient()
    assert client is not None


def test_create_client_with_config():
    """Test that we can create a SGUClient with custom configuration."""
    config = SGUConfig(timeout=30, log_level="DEBUG")
    client = SGUClient(config=config)
    assert client is not None


def test_client_context_manager():
    """Test that SGUClient works as a context manager."""
    with SGUClient() as client:
        assert client is not None


def test_client_fetches_through_the_given_transport() -> None:
    fake = FakeTransport(
        {"stationer/items/stationer.4086": create_mock_single_station_response()}
    )
    client = SGUClient(transport=fake)

    station = client.levels.observed.get_station("stationer.4086")

    assert station.id == "stationer.4086"
    assert fake.requests == [
        Request(f"{OBSERVED_URL}collections/stationer/items/stationer.4086", {})
    ]


def test_context_manager_closes_the_transport_it_created():
    with patch.object(RequestsTransport, "close") as close, SGUClient():
        close.assert_not_called()
    close.assert_called_once()


def test_close_closes_the_transport_it_created():
    client = SGUClient()
    with patch.object(RequestsTransport, "close") as close:
        client.close()
    close.assert_called_once()


def test_close_leaves_a_given_transport_open():
    fake = FakeTransport()
    with SGUClient(transport=fake):
        pass
    assert not fake.closed


def test_extra_keyword_arguments_are_sent_as_query_params() -> None:
    fake = FakeTransport({"stationer/items": create_mock_single_station_response()})
    client = SGUClient(transport=fake)

    client.levels.observed.get_stations(limit=1, properties="obsplatsnamn")

    assert fake.params == {"limit": 1, "properties": "obsplatsnamn"}
