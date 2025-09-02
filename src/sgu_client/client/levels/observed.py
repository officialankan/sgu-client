"""Observed groundwater level client endpoints."""

from sgu_client.client.base import BaseClient


class ObservedGroundwaterLevelClient:
    """Client for observed groundwater level-related SGU API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize observed groundwater level client.

        Args:
            base_client: Base HTTP client instance
        """
        self._client = base_client

    pass
