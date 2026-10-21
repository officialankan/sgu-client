"""Tests for how the client turns SGU's responses into data or errors."""

import logging

import pytest

from sgu_client import (
    SGUAPIError,
    SGUClient,
    SGUConfig,
    SGUConnectionError,
    SGUTimeoutError,
    TransportResponse,
)
from tests.fakes import FakeTransport, paged
from tests.mock_responses import create_mock_station_feature

STATIONS = "collections/stationer/items"
STATIONS_URL = (
    "https://api.sgu.se/oppnadata/grundvattennivaer-observerade/ogc/features/v1/"
    + STATIONS
)


def client_with(*responses) -> SGUClient:
    fake = FakeTransport({STATIONS: list(responses)})
    # log_level=None leaves logging alone, so caplog keeps its handler
    return SGUClient(config=SGUConfig(log_level=None), transport=fake)


def test_debug_logs_each_request(caplog):
    client = client_with(*paged([create_mock_station_feature()], page_size=1))

    with caplog.at_level(logging.DEBUG, logger="sgu_client.client.base"):
        client.levels.observed.get_stations(limit=1)

    assert f"Making GET request to {STATIONS_URL}" in caplog.text
    assert "Query params: {'limit': 1}" in caplog.text
    assert "Response status: 200" in caplog.text


def test_debug_logs_pagination(caplog):
    features = [create_mock_station_feature(f"stationer.{i}") for i in range(15)]
    client = client_with(*paged(features, page_size=10))

    with caplog.at_level(logging.DEBUG, logger="sgu_client.client.base"):
        client.levels.observed.get_stations()

    assert "Pagination needed: 10/15 features matched" in caplog.text
    assert "Pagination complete: 15 total features collected" in caplog.text


def test_an_error_status_raises_with_the_json_body():
    client = client_with(TransportResponse(404, '{"error": "Not Found"}'))

    with pytest.raises(SGUAPIError, match="API request failed with status 404") as e:
        client.levels.observed.get_stations()

    assert e.value.status_code == 404
    assert e.value.response_data == {"error": "Not Found"}


def test_an_error_status_without_json_keeps_the_text():
    client = client_with(TransportResponse(502, "<html>Bad Gateway</html>"))

    with pytest.raises(SGUAPIError) as e:
        client.levels.observed.get_stations()

    assert e.value.status_code == 502
    assert e.value.response_data == {"error": "<html>Bad Gateway</html>"}


def test_invalid_json_on_success_raises_api_error():
    client = client_with(TransportResponse(200, "not json"))

    with pytest.raises(SGUAPIError, match="Request failed"):
        client.levels.observed.get_stations()


@pytest.mark.parametrize(
    "error",
    [SGUTimeoutError("Read timeout after 30s"), SGUConnectionError("refused")],
)
def test_transport_errors_reach_the_caller_unchanged(error):
    client = client_with(error)

    with pytest.raises(type(error)) as e:
        client.levels.observed.get_stations()

    assert e.value is error
