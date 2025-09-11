"""Observed groundwater level client endpoints."""

import logging
from datetime import datetime
from typing import Any

from sgu_client.client.base import BaseClient
from sgu_client.models.observed import (
    GroundwaterMeasurement,
    GroundwaterMeasurementCollection,
    GroundwaterStation,
    GroundwaterStationCollection,
)

logger = logging.getLogger(__name__)


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
            limit: Maximum number of features to return (automatically paginated if needed)
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
            limit: Maximum number of features to return (automatically paginated if needed)
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

    def get_station_by_name(
        self,
        platsbeteckning: str | None = None,
        obsplatsnamn: str | None = None,
        **kwargs: Any,
    ) -> GroundwaterStation:
        """Convenience function to get a station by name ('platsbeteckning' or 'obsplatsnamn').

        Args:
            platsbeteckning: Station 'platsbeteckning' value
            obsplatsnamn: Station 'obsplatsnamn' value
            **kwargs: Additional query parameters (e.g., limit)

        Returns:
            Typed groundwater monitoring station

        Raises:
            ValueError: If neither parameter is provided, both are provided,
                       or if multiple stations are found
        """
        if not platsbeteckning and not obsplatsnamn:
            raise ValueError(
                "Either 'platsbeteckning' or 'obsplatsnamn' must be provided."
            )
        if platsbeteckning and obsplatsnamn:
            raise ValueError(
                "Only one of 'platsbeteckning' or 'obsplatsnamn' can be provided."
            )

        name_type = "platsbeteckning" if platsbeteckning else "obsplatsnamn"
        station = platsbeteckning if platsbeteckning else obsplatsnamn
        filter_expr = f"{name_type}='{station}'"
        response = self.get_stations(filter_expr=filter_expr, **kwargs)
        if len(response.features) > 1:
            raise ValueError(f"Multiple stations found for {filter_expr}")
        return response.features[0]

    def get_stations_by_names(
        self,
        platsbeteckning: list[str] | None = None,
        obsplatsnamn: list[str] | None = None,
        **kwargs: Any,
    ) -> GroundwaterStationCollection:
        """Convenience function to get multiple stations by name ('platsbeteckning' or 'obsplatsnamn').

        Args:
            platsbeteckning: List of station 'platsbeteckning' values
            obsplatsnamn: List of station 'obsplatsnamn' values
            **kwargs: Additional query parameters (e.g., limit)

        Returns:
            Typed collection of groundwater monitoring stations

        Raises:
            ValueError: If neither parameter is provided or both are provided
        """
        if not platsbeteckning and not obsplatsnamn:
            raise ValueError(
                "Either 'platsbeteckningar' or 'obsplatsnamn' must be provided."
            )
        if platsbeteckning and obsplatsnamn:
            raise ValueError(
                "Only one of 'platsbeteckningar' or 'obsplatsnamn' can be provided."
            )

        name_type = "platsbeteckning" if platsbeteckning else "obsplatsnamn"
        stations = platsbeteckning if platsbeteckning else obsplatsnamn

        # Build filter expression for multiple stations using IN clause
        # stations is guaranteed to not be None by the validation above
        quoted_stations = [f"'{station}'" for station in stations]  # type: ignore[union-attr]
        filter_expr = f"{name_type} in ({', '.join(quoted_stations)})"

        return self.get_stations(filter_expr=filter_expr, **kwargs)

    def get_measurements_by_name(
        self,
        platsbeteckning: str | None = None,
        obsplatsnamn: str | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> GroundwaterMeasurementCollection:
        """Get measurements for a specific station by name with optional time filtering.

        Args:
            platsbeteckning: Station 'platsbeteckning' value
            obsplatsnamn: Station 'obsplatsnamn' value
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)
            limit: Maximum number of measurements to return
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater level measurements

        Raises:
            ValueError: If neither or both name parameters are provided,
                       or if station lookup fails
        """
        if not platsbeteckning and not obsplatsnamn:
            raise ValueError(
                "Either 'platsbeteckning' or 'obsplatsnamn' must be provided."
            )
        if platsbeteckning and obsplatsnamn:
            raise ValueError(
                "Only one of 'platsbeteckning' or 'obsplatsnamn' can be provided."
            )

        # If obsplatsnamn provided, look up the station to get platsbeteckning
        if obsplatsnamn:
            logger.warning(
                "Using 'obsplatsnamn' requires an additional API request to lookup the station. "
                "For better performance, use 'platsbeteckning' directly if available."
            )
            # Don't pass kwargs to station lookup as it's a single result operation
            station = self.get_station_by_name(obsplatsnamn=obsplatsnamn)
            target_platsbeteckning = station.properties.platsbeteckning
            if not target_platsbeteckning:
                raise ValueError(
                    f"Station with obsplatsnamn '{obsplatsnamn}' has no platsbeteckning"
                )
        else:
            target_platsbeteckning = platsbeteckning

        # Build filter expressions
        filters = [f"platsbeteckning='{target_platsbeteckning}'"]

        # Add datetime filters if tmin/tmax provided
        datetime_filters = self._build_datetime_filters(tmin, tmax)
        filters.extend(datetime_filters)

        # Combine all filters with AND
        combined_filter = " AND ".join(filters)

        return self.get_measurements(
            filter_expr=combined_filter,
            limit=limit,
            **kwargs,
        )

    def get_measurements_by_names(
        self,
        platsbeteckning: list[str] | None = None,
        obsplatsnamn: list[str] | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> GroundwaterMeasurementCollection:
        """Get measurements for multiple stations by name with optional time filtering.

        Args:
            platsbeteckning: List of station 'platsbeteckning' values
            obsplatsnamn: List of station 'obsplatsnamn' values
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)
            limit: Maximum number of measurements to return
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater level measurements

        Raises:
            ValueError: If neither or both name parameters are provided,
                       or if station lookup fails
        """
        if not platsbeteckning and not obsplatsnamn:
            raise ValueError(
                "Either 'platsbeteckning' or 'obsplatsnamn' must be provided."
            )
        if platsbeteckning and obsplatsnamn:
            raise ValueError(
                "Only one of 'platsbeteckning' or 'obsplatsnamn' can be provided."
            )

        # If obsplatsnamn provided, look up stations to get platsbeteckning values
        if obsplatsnamn:
            logger.warning(
                "Using 'obsplatsnamn' requires an additional API request to lookup stations. "
                "For better performance, use 'platsbeteckning' directly if available."
            )
            # Don't pass kwargs to station lookup as it's a separate operation
            stations = self.get_stations_by_names(obsplatsnamn=obsplatsnamn)
            target_platsbeteckningar = []
            for station in stations.features:
                if station.properties.platsbeteckning:
                    target_platsbeteckningar.append(station.properties.platsbeteckning)
                else:
                    raise ValueError(
                        f"Station {station.id} with obsplatsnamn '{station.properties.obsplatsnamn}' "
                        f"has no platsbeteckning"
                    )
        else:
            target_platsbeteckningar = platsbeteckning

        # Build filter expressions
        # target_platsbeteckningar is guaranteed to not be None by validation above
        quoted_stations = [f"'{station}'" for station in target_platsbeteckningar]  # type: ignore[union-attr]
        filters = [f"platsbeteckning in ({', '.join(quoted_stations)})"]

        # Add datetime filters if tmin/tmax provided
        datetime_filters = self._build_datetime_filters(tmin, tmax)
        filters.extend(datetime_filters)

        # Combine all filters with AND
        combined_filter = " AND ".join(filters)

        return self.get_measurements(
            filter_expr=combined_filter,
            limit=limit,
            **kwargs,
        )

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

    def _build_datetime_filters(
        self, tmin: str | datetime | None, tmax: str | datetime | None
    ) -> list[str]:
        """Build CQL datetime filter expressions from tmin/tmax parameters.

        Args:
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)

        Returns:
            List of CQL filter expressions for datetime constraints
        """
        filters = []

        # Convert datetime objects to ISO strings
        def to_iso_string(dt: str | datetime | None) -> str | None:
            if dt is None:
                return None
            if isinstance(dt, datetime):
                return dt.isoformat()
            return dt

        if tmin:
            tmin_str = to_iso_string(tmin)
            filters.append(f"obsdatum >= '{tmin_str}'")

        if tmax:
            tmax_str = to_iso_string(tmax)
            filters.append(f"obsdatum <= '{tmax_str}'")

        return filters

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
