"""Modeled groundwater level client endpoints."""

import logging
from typing import Any

from sgu_client.client.base import BaseClient
from sgu_client.client.collection import SGUCollection
from sgu_client.models.modeled import (
    ModeledArea,
    ModeledAreaCollection,
    ModeledGroundwaterLevel,
    ModeledGroundwaterLevelCollection,
)

logger = logging.getLogger(__name__)

DATASET = "grundvattennivaer-sgu-hype-omraden"


class ModeledGroundwaterLevelClient:
    """Client for modeled groundwater level-related SGU API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize modeled groundwater level client.

        Args:
            base_client: Base HTTP client instance
        """
        self._client = base_client
        self._areas = SGUCollection(
            base_client,
            dataset=DATASET,
            name="omraden",
            model=ModeledAreaCollection,
            label="Area",
        )
        self._levels = SGUCollection(
            base_client,
            dataset=DATASET,
            name="grundvattennivaer-tidigare",
            model=ModeledGroundwaterLevelCollection,
            label="Level",
        )

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
            >>> with SGUClient() as client:
            ...     # get all modeled areas
            ...     areas = client.levels.modeled.get_areas(limit=100)
            ...     # get areas in a specific region
            ...     areas = client.levels.modeled.get_areas(
            ...         bbox=[15.0, 58.0, 17.0, 60.0]
            ...     )
            ...     for area in areas.features:
            ...         print(f"area: {area.properties.area_id}")
        """
        return self._areas.query(
            bbox=bbox,
            limit=limit,
            filter_expr=filter_expr,
            sortby=sortby,
            **kwargs,
        )

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
        return self._areas.get(area_id)

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
            >>> with SGUClient() as client:
            ...     # get modeled levels
            ...     levels = client.levels.modeled.get_levels(limit=100)
            ...     # get levels for a specific time period
            ...     levels = client.levels.modeled.get_levels(
            ...         datetime="2023-01-01/2024-01-01",
            ...         limit=1000
            ...     )
        """
        return self._levels.query(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter_expr=filter_expr,
            sortby=sortby,
            **kwargs,
        )

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
        return self._levels.get(level_id)

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
            >>> with SGUClient() as client:
            ...     # get all modeled levels for a specific area
            ...     levels = client.levels.modeled.get_levels_by_area(
            ...         area_id=30125,
            ...         limit=500
            ...     )
            ...     # with time filtering
            ...     levels = client.levels.modeled.get_levels_by_area(
            ...         area_id=30125,
            ...         datetime="2023-01-01/2024-01-01"
            ...     )
        """
        return self._levels.query(where={"omrade_id": int(area_id)}, **kwargs)

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
            >>> with SGUClient() as client:
            ...     levels = client.levels.modeled.get_levels_by_areas(
            ...         area_ids=[30125, 30126],
            ...         datetime="2024-09-30/2025-10-01"
            ...     )
            ...     print(f"Found {len(levels.features)} modeled levels")
        """
        if not area_ids:
            raise ValueError("At least one area ID must be provided")

        return self._levels.query(
            where={"omrade_id": [int(area_id) for area_id in area_ids]}, **kwargs
        )

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
            >>> with SGUClient() as client:
            ...     # get modeled levels for a specific location (Stockholm)
            ...     levels = client.levels.modeled.get_levels_by_coords(
            ...         lat=59.33,
            ...         lon=18.07,
            ...         limit=100
            ...     )
            ...     # increase buffer for larger search area
            ...     levels = client.levels.modeled.get_levels_by_coords(
            ...         lat=59.33,
            ...         lon=18.07,
            ...         buffer=0.05,  # ~5km radius
            ...         datetime="2023-01-01/2024-01-01"
            ...     )
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
