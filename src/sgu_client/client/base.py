"""Base HTTP client for SGU API."""

import logging
from typing import Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from sgu_client.config import SGUConfig, setup_logging
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

        # Configure logging based on config
        setup_logging(self.config.log_level)

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
        base_url: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make an HTTP request to the SGU API with automatic pagination.

        This method automatically handles pagination for OGC API Features responses
        by detecting when the API returns fewer features than available and making
        additional requests to fetch all remaining data.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            data: Request body data
            base_url: Optional override for base URL (for different API endpoints)
            **kwargs: Additional arguments passed to requests

        Returns:
            JSON response data with all features if pagination was applied

        Raises:
            SGUConnectionError: If connection fails
            SGUTimeoutError: If request times out
            SGUAPIError: If API returns an error
        """
        url = urljoin(base_url or self.config.base_url, endpoint)
        params = params or {}

        try:
            logger.debug(f"Making {method} request to {url}")
            if params:
                logger.debug(f"Query params: {params}")
            if data:
                logger.debug(f"Request data: {data}")

            # Make initial request
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                timeout=self.config.timeout,
                **kwargs,
            )

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

            response_data = response.json()

            # Check if this is a GeoJSON FeatureCollection that may need pagination
            if (
                method.upper() == "GET"
                and response_data.get("type") == "FeatureCollection"
                and "features" in response_data
            ):
                response_data = self._handle_pagination(
                    url, params, response_data, **kwargs
                )

            return response_data

        except requests.exceptions.ReadTimeout as e:
            raise SGUTimeoutError(f"Read timeout after {self.config.timeout}s") from e
        except requests.exceptions.ConnectTimeout as e:
            raise SGUTimeoutError(
                f"Connection timeout after {self.config.timeout}s"
            ) from e
        except requests.exceptions.ConnectionError as e:
            # Check if this is a timeout wrapped in MaxRetryError
            if "Read timed out" in str(e) or "ReadTimeoutError" in str(e):
                raise SGUTimeoutError(
                    f"Read timeout after {self.config.timeout}s"
                ) from e
            raise SGUConnectionError(f"Connection failed: {e}") from e
        except requests.exceptions.RequestException as e:
            raise SGUAPIError(f"Request failed: {e}") from e

    def _handle_pagination(
        self,
        url: str,
        initial_params: dict[str, Any],
        initial_response: dict[str, Any],
        **kwargs,
    ) -> dict[str, Any]:
        """Handle automatic pagination for OGC API Features responses.

        Args:
            url: The request URL
            initial_params: Parameters from the initial request
            initial_response: Response from the initial request
            **kwargs: Additional arguments passed to requests

        Returns:
            Combined response with all features
        """
        # Check if pagination is needed
        number_returned = initial_response.get("numberReturned", 0)
        number_matched = initial_response.get("numberMatched") or initial_response.get(
            "totalFeatures"
        )

        # Handle cases where API returns 'unknown' or other non-numeric values
        if isinstance(number_matched, str) and number_matched.lower() in (
            "unknown",
            "null",
        ):
            number_matched = None

        if (
            not number_matched
            or not isinstance(number_matched, int)
            or number_returned >= number_matched
        ):
            # No pagination needed
            return initial_response

        # Safety check: Don't auto-paginate beyond reasonable limits
        # If user requested a specific limit, respect it; otherwise use 50K as max
        user_requested_limit = initial_params.get("limit")
        max_features = min(number_matched, user_requested_limit or 50000)

        if number_returned >= max_features:
            # Already have enough features
            return initial_response

        logger.debug(
            f"Pagination needed: {number_returned}/{number_matched} features matched, "
            f"will fetch up to {max_features} features total"
        )

        # Collect all features
        all_features = initial_response["features"].copy()
        current_start_index = number_returned

        while current_start_index < max_features:
            # Prepare parameters for next page
            next_params = initial_params.copy()
            next_params["startIndex"] = current_start_index

            # Keep the same limit as the initial request (or use API default)
            if "limit" not in next_params:
                next_params["limit"] = (
                    number_returned  # Use same page size as first response
                )

            # Adjust limit for final page to not exceed max_features
            remaining = max_features - current_start_index
            if remaining < next_params["limit"]:
                next_params["limit"] = remaining

            logger.debug(f"Fetching page starting at index {current_start_index}")

            # Make request for next page
            response = self._session.request(
                method="GET",
                url=url,
                params=next_params,
                timeout=self.config.timeout,
                **kwargs,
            )

            if not response.ok:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"error": response.text}

                raise SGUAPIError(
                    f"Pagination request failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data,
                )

            page_data = response.json()
            page_features = page_data.get("features", [])

            if not page_features:
                # No more features to fetch
                break

            all_features.extend(page_features)
            current_start_index += len(page_features)

            logger.debug(
                f"Fetched {len(page_features)} features, total: {len(all_features)}"
            )

        # Update the response with all collected features
        final_response = initial_response.copy()
        final_response["features"] = all_features
        final_response["numberReturned"] = len(all_features)

        logger.debug(
            f"Pagination complete: {len(all_features)} total features collected"
        )

        return final_response

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        base_url: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make a GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            base_url: Optional override for base URL
            **kwargs: Additional arguments passed to requests

        Returns:
            JSON response data

        Raises:
            SGUConnectionError: If connection fails
            SGUTimeoutError: If request times out
            SGUAPIError: If API returns an error
        """
        return self._make_request(
            "GET", endpoint, params=params, base_url=base_url, **kwargs
        )

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
