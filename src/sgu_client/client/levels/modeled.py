"""Modeled groundwater level client endpoints."""

from typing import Any

from sgu_client.client.base import BaseClient
from sgu_client.config import SGUConfig
from sgu_client.models.modeled import (
    ModeledArea,
    ModeledAreaCollection,
    ModeledGroundwaterLevel,
    ModeledGroundwaterLevelCollection,
)


class ModeledGroundwaterLevelClient:
    """Client for modeled groundwater level-related SGU API endpoints."""

    BASE_PATH = "collections"

    def __init__(self, base_client: BaseClient):
        """Initialize modeled groundwater level client.

        Args:
            base_client: Base HTTP client instance
        """
        # Create a new client with modeled data API URL
        modeled_config = SGUConfig(
            base_url="https://api.sgu.se/oppnadata/grundvattennivaer-sgu-hype-omraden/ogc/features/v1/",
            timeout=base_client.config.timeout,
            max_retries=base_client.config.max_retries,
            user_agent=base_client.config.user_agent,
            debug=base_client.config.debug,
        )
        self._client = BaseClient(modeled_config)

    def get_areas(
        self,
        bbox: list[float] | None = None,
        limit: int | None = None,
        filter_expr: str | None = None,
        sortby: list[str] | None = None,
        **kwargs: Any,
    ) -> ModeledAreaCollection:
        """Get modeled groundwater areas.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            limit: Maximum number of features to return (1-50000, default 50000)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+omrade_id'])
            **kwargs: Additional query parameters

        Returns:
            Typed collection of modeled groundwater areas
        """
        endpoint = f"{self.BASE_PATH}/omraden/items"
        params = self._build_query_params(
            bbox=bbox,
            limit=limit,
            filter=filter_expr,
            sortby=sortby,
            **kwargs,
        )
        response = self._make_request(endpoint, params)
        return ModeledAreaCollection(**response)

    def get_area(self, area_id: str) -> ModeledArea:
        """Get a specific modeled groundwater area by ID.

        Args:
            area_id: Area identifier

        Returns:
            Typed modeled groundwater area

        Raises:
            ValueError: If area not found or multiple areas returned
        """
        endpoint = f"{self.BASE_PATH}/omraden/items/{area_id}"
        response = self._make_request(endpoint, {})

        # SGU API returns a FeatureCollection even for single items
        collection = ModeledAreaCollection(**response)
        if not collection.features:
            raise ValueError(f"Area {area_id} not found")
        if len(collection.features) > 1:
            raise ValueError(f"Multiple areas returned for ID {area_id}")

        return collection.features[0]

    def get_levels(
        self,
        bbox: list[float] | None = None,
        datetime: str | None = None,
        limit: int | None = None,
        filter_expr: str | None = None,
        sortby: list[str] | None = None,
        **kwargs: Any,
    ) -> ModeledGroundwaterLevelCollection:
        """Get modeled groundwater levels.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            datetime: Date/time filter (RFC 3339 format or interval)
            limit: Maximum number of features to return (1-50000, default 50000)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+datum', '-omrade_id'])
            **kwargs: Additional query parameters

        Returns:
            Typed collection of modeled groundwater levels
        """
        endpoint = f"{self.BASE_PATH}/grundvattennivaer-tidigare/items"
        params = self._build_query_params(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter=filter_expr,
            sortby=sortby,
            **kwargs,
        )
        response = self._make_request(endpoint, params)
        return ModeledGroundwaterLevelCollection(**response)

    def get_level(self, level_id: str) -> ModeledGroundwaterLevel:
        """Get a specific modeled groundwater level by ID.

        Args:
            level_id: Level identifier

        Returns:
            Typed modeled groundwater level

        Raises:
            ValueError: If level not found or multiple levels returned
        """
        endpoint = f"{self.BASE_PATH}/grundvattennivaer-tidigare/items/{level_id}"
        response = self._make_request(endpoint, {})

        # SGU API returns a FeatureCollection even for single items
        collection = ModeledGroundwaterLevelCollection(**response)
        if not collection.features:
            raise ValueError(f"Level {level_id} not found")
        if len(collection.features) > 1:
            raise ValueError(f"Multiple levels returned for ID {level_id}")

        return collection.features[0]

    # TODO: add convenience methods like `get_levels_by_area` and `get_levels_by_areas`

    def _build_query_params(self, **params: Any) -> dict[str, Any]:
        """Build query parameters for API requests.

        Args:
            **params: Raw parameter values

        Returns:
            Cleaned dictionary of query parameters
        """
        query_params = {}

        for key, value in params.items():
            if value is None:
                continue

            if key == "bbox" and isinstance(value, list):
                query_params[key] = ",".join(map(str, value))
            elif key == "sortby" and isinstance(value, list):
                query_params[key] = ",".join(value)
            else:
                query_params[key] = value

        return query_params

    def _make_request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
        """Make HTTP request to SGU API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            Various HTTP and API exceptions via base client
        """
        return self._client.get(endpoint, params=params)
