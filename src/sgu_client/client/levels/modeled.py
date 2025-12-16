"""Modeled groundwater level client endpoints."""

import logging
from typing import Any

from sgu_client.client.base import BaseClient
from sgu_client.models.modeled import (
    ModeledArea,
    ModeledAreaCollection,
    ModeledGroundwaterLevel,
    ModeledGroundwaterLevelCollection,
)

logger = logging.getLogger(__name__)


class ModeledGroundwaterLevelClient:
    """Client for modeled groundwater level-related SGU API endpoints."""

    BASE_PATH = "collections"
    MODELED_BASE_URL = "https://api.sgu.se/oppnadata/grundvattennivaer-sgu-hype-omraden/ogc/features/v1/"

    def __init__(self, base_client: BaseClient):
        """Initialize modeled groundwater level client.

        Args:
            base_client: Base HTTP client instance
        """
        self._client = base_client

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
            limit: Maximum number of features to return (automatically paginated if needed)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+omrade_id'] - use Swedish field names for API)
            **kwargs: Additional query parameters

        Returns:
            Typed collection of modeled groundwater areas

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get all modeled areas
            >>> areas = client.levels.modeled.get_areas(limit=100)
            >>>
            >>> # get areas in a specific region
            >>> areas = client.levels.modeled.get_areas(
            ...     bbox=[15.0, 58.0, 17.0, 60.0]
            ... )
            >>> for area in areas.features:
            ...     print(f"area: {area.properties.area_id}")
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
        """Get a specific modeled groundwater area by ID. This endpoint is provided by OGC API
        but not likely used by any user.

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
            limit: Maximum number of features to return (automatically paginated if needed)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+datum', '-omrade_id'] - use Swedish field names for API)
            **kwargs: Additional query parameters

        Returns:
            Typed collection of modeled groundwater levels

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get modeled levels
            >>> levels = client.levels.modeled.get_levels(limit=100)
            >>>
            >>> # get levels for a specific time period
            >>> levels = client.levels.modeled.get_levels(
            ...     datetime="2023-01-01/2024-01-01",
            ...     limit=1000
            ... )
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
        """Get a specific modeled groundwater level by ID. This endpoint is provided by the OGC API
        but not likely used by any user.

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

    def get_levels_by_area(
        self, area_id: int, **kwargs: Any
    ) -> ModeledGroundwaterLevelCollection:
        """Get modeled groundwater levels for a specific area.

        Args:
            area_id: Area ID to filter by
            **kwargs: Additional query parameters (limit, datetime, bbox, etc.)

        Returns:
            Typed collection of modeled groundwater levels for the specified area

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get all modeled levels for a specific area
            >>> levels = client.levels.modeled.get_levels_by_area(
            ...     area_id=30125,
            ...     limit=500
            ... )
            >>>
            >>> # with time filtering
            >>> levels = client.levels.modeled.get_levels_by_area(
            ...     area_id=30125,
            ...     datetime="2023-01-01/2024-01-01"
            ... )
        """
        filter_expr = f"omrade_id = {area_id}"
        return self.get_levels(filter_expr=filter_expr, **kwargs)

    def get_levels_by_areas(
        self, area_ids: list[int], **kwargs: Any
    ) -> ModeledGroundwaterLevelCollection:
        """Get modeled groundwater levels for multiple areas.

        Args:
            area_ids: List of area IDs to filter by
            **kwargs: Additional query parameters (limit, datetime, bbox, etc.)

        Returns:
            Typed collection of modeled groundwater levels for the specified areas

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>> levels = client.levels.modeled.get_levels_by_areas(
            ...     area_ids=[30125, 30126],
            ...     datetime="2024-09-31/2025-10-01"
            ... )
            >>> print(f"Found {len(levels.features)} modeled levels")
        """
        if not area_ids:
            raise ValueError("At least one area ID must be provided")

        # Create CQL filter expression for multiple area IDs
        if len(area_ids) == 1:
            filter_expr = f"omrade_id = {area_ids[0]}"
        else:
            area_ids_str = ", ".join(str(area_id) for area_id in area_ids)
            filter_expr = f"omrade_id IN ({area_ids_str})"

        return self.get_levels(filter_expr=filter_expr, **kwargs)

    def get_levels_by_coords(
        self,
        lat: float,
        lon: float,
        buffer: float = 0.01,
        **kwargs: Any,
    ) -> ModeledGroundwaterLevelCollection:
        """Get modeled groundwater levels for a specific coordinate.

        This convenience function first finds relevant areas containing or near
        the specified coordinates, then retrieves modeled levels for those areas.

        Args:
            lat: Latitude coordinate (WGS84)
            lon: Longitude coordinate (WGS84)
            buffer: Buffer distance in degrees around the point (default 0.01 ≈ 1km)
            **kwargs: Additional query parameters (limit, datetime, etc.)

        Returns:
            Typed collection of modeled groundwater levels for areas near the coordinates

        Raises:
            ValueError: If no areas found near the specified coordinates

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get modeled levels for a specific location (Stockholm)
            >>> levels = client.levels.modeled.get_levels_by_coords(
            ...     lat=59.33,
            ...     lon=18.07,
            ...     limit=100
            ... )
            >>>
            >>> # increase buffer for larger search area
            >>> levels = client.levels.modeled.get_levels_by_coords(
            ...     lat=59.33,
            ...     lon=18.07,
            ...     buffer=0.05,  # ~5km radius
            ...     datetime="2023-01-01/2024-01-01"
            ... )
        """
        # Create bounding box around the point
        bbox = [
            lon - buffer,  # min_lon
            lat - buffer,  # min_lat
            lon + buffer,  # max_lon
            lat + buffer,  # max_lat
        ]

        # Find areas within the bounding box
        areas = self.get_areas(bbox=bbox, limit=1000)

        if not areas.features:
            raise ValueError(
                f"No modeled groundwater areas found near coordinates "
                f"({lat}, {lon}) within {buffer}° buffer"
            )

        # Extract area IDs
        area_ids = [int(area.properties.area_id) for area in areas.features]

        # Log warning if multiple areas found (near boundary)
        if len(area_ids) > 1:
            # Show subset of area_ids if list is long
            if len(area_ids) > 10:
                area_ids_display = (
                    f"{area_ids[:5]} ... {area_ids[-5:]} ({len(area_ids)} total)"
                )
            else:
                area_ids_display = str(area_ids)
            logger.warning(
                f"Found {len(area_ids)} modeled areas near coordinates "
                f"({lat}, {lon}). This suggests the point is close to an area boundary "
                f"or that you have a large buffer. "
                f"Area IDs: {area_ids_display}. All areas will be included in the results."
            )

        # Get levels for all found areas
        return self.get_levels_by_areas(area_ids, **kwargs)

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
        return self._client.get(endpoint, params=params, base_url=self.MODELED_BASE_URL)
