"""Base client for SGU API: requests, errors and pagination."""

import json
import logging
from typing import Any
from urllib.parse import urljoin

from sgu_client.config import SGUConfig, setup_logging
from sgu_client.exceptions import SGUAPIError
from sgu_client.transport import RequestsTransport, Transport

logger = logging.getLogger(__name__)

# Safety cap on automatic pagination when the caller sets no limit
MAX_FEATURES = 50000


class BaseClient:
    """Sends GET requests to SGU through a transport and pages through results.

    Args:
        config: Configuration object. If None, uses default config.
        transport: Where requests go. If None, a :class:`RequestsTransport` is
            built from the config and closed by :meth:`close`. A transport you
            pass in is yours to close.
    """

    def __init__(
        self, config: SGUConfig | None = None, transport: Transport | None = None
    ):
        self.config = config or SGUConfig()
        self._owned_transport: RequestsTransport | None = None
        if transport is None:
            self._owned_transport = transport = RequestsTransport(self.config)
        self._transport = transport

        # Configure logging based on config
        setup_logging(self.config.log_level)

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        base_url: str | None = None,
    ) -> dict[str, Any]:
        """GET an endpoint, fetching every page of a FeatureCollection.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            base_url: Optional override for base URL (for different API endpoints)

        Returns:
            JSON response data, with all features if the response was paginated

        Raises:
            SGUConnectionError: If connection fails
            SGUTimeoutError: If request times out
            SGUAPIError: If API returns an error
        """
        url = urljoin(base_url or self.config.base_url, endpoint)
        params = params or {}

        logger.debug(f"Making GET request to {url}")
        if params:
            logger.debug(f"Query params: {params}")

        data = self._fetch_page(url, params, failure="API request failed")
        if data.get("type") == "FeatureCollection" and "features" in data:
            data = self._handle_pagination(url, params, data)
        return data

    def _fetch_page(
        self, url: str, params: dict[str, Any], *, failure: str
    ) -> dict[str, Any]:
        response = self._transport.fetch(url, params)
        logger.debug(f"Response status: {response.status_code}")

        if response.status_code >= 400:
            try:
                error_data = json.loads(response.text)
            except ValueError:
                error_data = {"error": response.text}
            raise SGUAPIError(
                f"{failure} with status {response.status_code}",
                status_code=response.status_code,
                response_data=error_data,
            )

        try:
            return json.loads(response.text)
        except ValueError as e:
            raise SGUAPIError(f"Request failed: {e}") from e

    def _handle_pagination(
        self,
        url: str,
        initial_params: dict[str, Any],
        initial_response: dict[str, Any],
    ) -> dict[str, Any]:
        """Fetch the remaining pages of an OGC API Features response.

        Args:
            url: The request URL
            initial_params: Parameters from the initial request
            initial_response: Response from the initial request

        Returns:
            Combined response with all features
        """
        number_returned = initial_response.get("numberReturned", 0)
        number_matched = initial_response.get("numberMatched") or initial_response.get(
            "totalFeatures"
        )

        # SGU sends "unknown" when it doesn't count the matches; we can't page then
        if (
            not number_matched
            or not isinstance(number_matched, int)
            or number_returned >= number_matched
        ):
            return initial_response

        # Respect a limit the caller set; otherwise stop at the safety cap
        user_requested_limit = initial_params.get("limit")
        max_features = min(number_matched, user_requested_limit or MAX_FEATURES)

        if number_returned >= max_features:
            return initial_response

        logger.debug(
            f"Pagination needed: {number_returned}/{number_matched} features matched, "
            f"will fetch up to {max_features} features total"
        )

        all_features = initial_response["features"].copy()
        current_start_index = number_returned

        while current_start_index < max_features:
            next_params = initial_params.copy()
            next_params["startIndex"] = current_start_index

            # Keep the page size of the first response unless the caller set one
            if "limit" not in next_params:
                next_params["limit"] = number_returned

            # Don't fetch past max_features on the last page
            remaining = max_features - current_start_index
            if remaining < next_params["limit"]:
                next_params["limit"] = remaining

            logger.debug(f"Fetching page starting at index {current_start_index}")

            page_data = self._fetch_page(
                url, next_params, failure="Pagination request failed"
            )
            page_features = page_data.get("features", [])

            if not page_features:
                break

            all_features.extend(page_features)
            current_start_index += len(page_features)

            logger.debug(
                f"Fetched {len(page_features)} features, total: {len(all_features)}"
            )

        final_response = initial_response.copy()
        final_response["features"] = all_features
        final_response["numberReturned"] = len(all_features)

        logger.debug(
            f"Pagination complete: {len(all_features)} total features collected"
        )

        return final_response

    def close(self) -> None:
        """Close the transport, if this client created it."""
        if self._owned_transport is not None:
            self._owned_transport.close()

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
        self.close()
