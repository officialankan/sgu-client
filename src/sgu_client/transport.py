"""How sgu-client reaches SGU: one page of a response per request.

:class:`SGUClient <sgu_client.SGUClient>` sends every request through a
:class:`Transport`. The default, :class:`RequestsTransport`, talks to SGU over the
network. Pass your own to ``SGUClient(transport=...)`` to serve responses from
somewhere else, such as canned pages in your tests.
"""

from dataclasses import dataclass
from typing import Any, Protocol

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from sgu_client.config import SGUConfig
from sgu_client.exceptions import SGUAPIError, SGUConnectionError, SGUTimeoutError


@dataclass(frozen=True)
class TransportResponse:
    """What SGU sent back for one request.

    Attributes:
        status_code: HTTP status code, e.g. ``200`` or ``404``
        text: Response body, usually JSON
    """

    status_code: int
    text: str


class Transport(Protocol):
    """Fetches one response from SGU.

    The client builds the URL and query params, then decides what the response
    means: it turns error statuses into :class:`~sgu_client.SGUAPIError`, parses
    the JSON and requests further pages.

    A transport raises :class:`~sgu_client.SGUTimeoutError` or
    :class:`~sgu_client.SGUConnectionError` when it can't get a response at all.
    """

    def fetch(self, url: str, params: dict[str, Any]) -> TransportResponse:
        """GET ``url`` with query ``params`` and return the response."""
        ...


class RequestsTransport:
    """The default transport: GET requests to SGU with the ``requests`` library.

    Uses ``timeout``, ``max_retries`` and ``user_agent`` from the config.
    Retries on 429 and 5xx responses with exponential backoff.

    Args:
        config: Configuration object. If None, uses default config.
    """

    def __init__(self, config: SGUConfig | None = None):
        self._config = config or SGUConfig()
        self._session = requests.Session()
        self._session.headers.update(
            {"User-Agent": self._config.user_agent, "Accept": "application/json"}
        )
        retries = Retry(
            total=self._config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def fetch(self, url: str, params: dict[str, Any]) -> TransportResponse:
        """GET ``url`` with query ``params`` and return the response.

        Raises:
            SGUTimeoutError: If connecting or reading times out.
            SGUConnectionError: If SGU can't be reached.
            SGUAPIError: If the request fails in any other way.
        """
        timeout = self._config.timeout
        try:
            response = self._session.get(url, params=params, timeout=timeout)
        except requests.exceptions.ReadTimeout as e:
            raise SGUTimeoutError(f"Read timeout after {timeout}s") from e
        except requests.exceptions.ConnectTimeout as e:
            raise SGUTimeoutError(f"Connection timeout after {timeout}s") from e
        except requests.exceptions.ConnectionError as e:
            # urllib3 reports a read timeout that ran out of retries as a
            # ConnectionError wrapping MaxRetryError
            if "Read timed out" in str(e) or "ReadTimeoutError" in str(e):
                raise SGUTimeoutError(f"Read timeout after {timeout}s") from e
            raise SGUConnectionError(f"Connection failed: {e}") from e
        except requests.exceptions.RequestException as e:
            raise SGUAPIError(f"Request failed: {e}") from e
        # JSON is UTF-8 (RFC 8259); don't let requests guess from the Content-Type
        text = response.content.decode("utf-8", errors="replace")
        return TransportResponse(response.status_code, text)

    def close(self) -> None:
        """Close the HTTP session and its pooled connections."""
        self._session.close()
