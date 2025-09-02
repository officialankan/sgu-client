"""Observed groundwater level client endpoints."""

from typing import Any

from sgu_client.client.base import BaseClient
from sgu_client.models.observed import (
    GroundwaterMeasurement,
    GroundwaterMeasurementCollection,
    GroundwaterStation,
    GroundwaterStationCollection,
)


class ObservedGroundwaterLevelClient:
    """Client for observed groundwater level-related SGU API endpoints."""

    BASE_PATH = "collections"

    def __init__(self, base_client: BaseClient):
        """Initialize observed groundwater level client.

        Args:
            base_client: Base HTTP client instance
        """
        self._client = base_client

    def get_stations(
        self,
        bbox: list[float] | None = None,
        datetime: str | None = None,
        limit: int | None = None,
        filter_expr: str | None = None,
        sortby: list[str] | None = None,
        **kwargs: Any,
    ) -> GroundwaterStationCollection:
        """Get groundwater monitoring stations.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            datetime: Date/time filter (RFC 3339 format or interval)
            limit: Maximum number of features to return (1-50000, default 50000)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+name', '-date'])
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater monitoring stations
        """
        endpoint = f"{self.BASE_PATH}/stationer/items"
        params = self._build_query_params(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter=filter_expr,
            sortby=sortby,
            **kwargs,
        )
        response = self._make_request(endpoint, params)
        return GroundwaterStationCollection(**response)

    def get_station(self, station_id: str) -> GroundwaterStation:
        """Get a specific groundwater monitoring station by ID.

        Args:
            station_id: Station identifier

        Returns:
            Typed groundwater monitoring station

        Raises:
            ValueError: If station not found or multiple stations returned
        """
        endpoint = f"{self.BASE_PATH}/stationer/items/{station_id}"
        response = self._make_request(endpoint, {})

        # SGU API returns a FeatureCollection even for single items
        collection = GroundwaterStationCollection(**response)
        if not collection.features:
            raise ValueError(f"Station {station_id} not found")
        if len(collection.features) > 1:
            raise ValueError(f"Multiple stations returned for ID {station_id}")

        return collection.features[0]

    def get_measurements(
        self,
        bbox: list[float] | None = None,
        datetime: str | None = None,
        limit: int | None = None,
        filter_expr: str | None = None,
        sortby: list[str] | None = None,
        **kwargs: Any,
    ) -> GroundwaterMeasurementCollection:
        """Get groundwater level measurements.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            datetime: Date/time filter (RFC 3339 format or interval)
            limit: Maximum number of features to return (1-50000, default 50000)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+date', '-value'])
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater level measurements
        """
        endpoint = f"{self.BASE_PATH}/nivaer/items"
        params = self._build_query_params(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter=filter_expr,
            sortby=sortby,
            **kwargs,
        )
        response = self._make_request(endpoint, params)
        return GroundwaterMeasurementCollection(**response)

    def get_measurement(self, measurement_id: str) -> GroundwaterMeasurement:
        """Get a specific groundwater level measurement by ID.

        Args:
            measurement_id: Measurement identifier

        Returns:
            Typed groundwater level measurement

        Raises:
            ValueError: If measurement not found or multiple measurements returned
        """
        endpoint = f"{self.BASE_PATH}/nivaer/items/{measurement_id}"
        response = self._make_request(endpoint, {})

        # SGU API returns a FeatureCollection even for single items
        collection = GroundwaterMeasurementCollection(**response)
        if not collection.features:
            raise ValueError(f"Measurement {measurement_id} not found")
        if len(collection.features) > 1:
            raise ValueError(f"Multiple measurements returned for ID {measurement_id}")

        return collection.features[0]

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
