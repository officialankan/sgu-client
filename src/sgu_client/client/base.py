"""Base HTTP client for SGU API."""

import logging
from typing import Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from sgu_client.config import SGUConfig
from sgu_client.exceptions import SGUAPIError, SGUConnectionError, SGUTimeoutError

logger = logging.getLogger(__name__)


class BaseClient:
    """Base HTTP client with common functionality for SGU API."""

    def __init__(self, config: SGUConfig | None = None):
        """Initialize the base client.

        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or SGUConfig()
        self._session = self._create_session()

        if self.config.debug:
            logging.basicConfig(level=logging.DEBUG)

    def _create_session(self) -> requests.Session:
        """Create and configure a requests session."""
        session = requests.Session()

        # Set headers
        session.headers.update(
            {
                "User-Agent": self.config.user_agent,
                "Accept": "application/json",
            }
        )

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make an HTTP request to the SGU API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            **kwargs: Additional arguments passed to requests

        Returns:
            JSON response data

        Raises:
            SGUConnectionError: If connection fails
            SGUTimeoutError: If request times out
            SGUAPIError: If API returns an error
        """
        url = urljoin(self.config.base_url, endpoint)

        try:
            if self.config.debug:
                logger.debug(f"Making {method} request to {url}")
                if params:
                    logger.debug(f"Query params: {params}")
                if data:
                    logger.debug(f"Request data: {data}")

            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.config.timeout,
                **kwargs,
            )

            if self.config.debug:
                logger.debug(f"Response status: {response.status_code}")

            # Check for HTTP errors
            if not response.ok:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"error": response.text}

                raise SGUAPIError(
                    f"API request failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data,
                )

            return response.json()

        except requests.exceptions.ConnectTimeout as e:
            raise SGUTimeoutError(
                f"Connection timeout after {self.config.timeout}s"
            ) from e
        except requests.exceptions.ReadTimeout as e:
            raise SGUTimeoutError(f"Read timeout after {self.config.timeout}s") from e
        except requests.exceptions.ConnectionError as e:
            raise SGUConnectionError(f"Connection failed: {e}") from e
        except requests.exceptions.RequestException as e:
            raise SGUAPIError(f"Request failed: {e}") from e

    def get(
        self, endpoint: str, params: dict[str, Any] | None = None, **kwargs
    ) -> dict[str, Any]:
        """Make a GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional arguments passed to requests

        Returns:
            JSON response data

        Raises:
            SGUConnectionError: If connection fails
            SGUTimeoutError: If request times out
            SGUAPIError: If API returns an error
        """
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(
        self, endpoint: str, data: dict[str, Any] | None = None, **kwargs
    ) -> dict[str, Any]:
        """Make a POST request.

        Args:
            endpoint: API endpoint path
            data: Request body data
            **kwargs: Additional arguments passed to requests

        Returns:
            JSON response data

        Raises:
            SGUConnectionError: If connection fails
            SGUTimeoutError: If request times out
            SGUAPIError: If API returns an error
        """
        return self._make_request("POST", endpoint, data=data, **kwargs)

    def __enter__(self):
        """Context manager entry.

        Returns:
            The client instance for use in with statements
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clean up resources.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        self._session.close()
