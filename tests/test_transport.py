"""Tests for RequestsTransport, the default transport.

This is the only test module that mocks ``requests``; everything else goes
through ``SGUClient(transport=FakeTransport(...))``.
"""

from unittest.mock import Mock, patch

import pytest
import requests
from pytest_socket import SocketBlockedError

from sgu_client import (
    RequestsTransport,
    SGUAPIError,
    SGUConfig,
    SGUConnectionError,
    SGUTimeoutError,
    TransportResponse,
)

URL = "https://api.example.com/test"


@pytest.fixture
def transport():
    return RequestsTransport(SGUConfig(timeout=12))


def test_returns_status_and_body_without_judging_them(transport):
    response = Mock(status_code=404, content=b'{"error": "Not Found"}')
    with patch.object(transport._session, "request", return_value=response):
        result = transport.fetch(URL, {"limit": 1})

    assert result == TransportResponse(404, '{"error": "Not Found"}')


def test_decodes_the_body_as_utf8_whatever_the_content_type(transport):
    # JSON is always UTF-8; requests would guess the charset for e.g. geo+json
    body = '{"kommun": "Mölndal"}'.encode()
    response = Mock(status_code=200, content=body, text=body.decode("latin-1"))
    with patch.object(transport._session, "request", return_value=response):
        result = transport.fetch(URL, {})

    assert result.text == '{"kommun": "Mölndal"}'


def test_sends_a_get_with_params_and_the_configured_timeout(transport):
    response = Mock(status_code=200, content=b"{}")
    with patch.object(transport._session, "request", return_value=response) as request:
        transport.fetch(URL, {"limit": 1})

    args, kwargs = request.call_args
    assert args == ("GET", URL)
    assert kwargs["params"] == {"limit": 1}
    assert kwargs["timeout"] == 12


def test_sends_the_configured_user_agent_and_asks_for_json():
    transport = RequestsTransport(SGUConfig(user_agent="my-app/1.0"))

    assert transport._session.headers["User-Agent"] == "my-app/1.0"
    assert transport._session.headers["Accept"] == "application/json"


def test_retries_rate_limits_and_server_errors_up_to_max_retries():
    transport = RequestsTransport(SGUConfig(max_retries=5))

    retries = transport._session.get_adapter("https://api.sgu.se").max_retries
    assert retries.total == 5
    assert set(retries.status_forcelist) == {429, 500, 502, 503, 504}


@pytest.mark.parametrize(
    ("raised", "expected", "message"),
    [
        (
            requests.exceptions.ReadTimeout("x"),
            SGUTimeoutError,
            "Read timeout after 12",
        ),
        (
            requests.exceptions.ConnectTimeout("x"),
            SGUTimeoutError,
            "Connection timeout after 12",
        ),
        # read timeouts that ran out of retries arrive as ConnectionError
        (
            requests.exceptions.ConnectionError("Read timed out"),
            SGUTimeoutError,
            "Read timeout after 12",
        ),
        (
            requests.exceptions.ConnectionError("ReadTimeoutError in connection"),
            SGUTimeoutError,
            "Read timeout after 12",
        ),
        (
            requests.exceptions.ConnectionError("Network unreachable"),
            SGUConnectionError,
            "Connection failed",
        ),
        (
            requests.exceptions.RequestException("Something went wrong"),
            SGUAPIError,
            "Request failed",
        ),
    ],
)
def test_network_failures_become_sgu_errors(transport, raised, expected, message):
    with (
        patch.object(transport._session, "request", side_effect=raised),
        pytest.raises(expected, match=message),
    ):
        transport.fetch(URL, {})


def test_close_closes_the_session(transport):
    with patch.object(transport._session, "close") as close:
        transport.close()
    close.assert_called_once()


@pytest.mark.filterwarnings("ignore:A test tried to use socket")
def test_tests_cannot_reach_the_network():
    """pytest-socket blocks sockets in every test except tests/test_actual_api.py."""
    with pytest.raises(SocketBlockedError):
        RequestsTransport().fetch("https://api.sgu.se/oppnadata/", {})
