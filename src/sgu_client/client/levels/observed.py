"""Observed groundwater level client endpoints."""

import logging
from datetime import datetime
from typing import Any

from sgu_client.client.base import BaseClient
from sgu_client.client.collection import SGUCollection
from sgu_client.models.observed import (
    GroundwaterMeasurement,
    GroundwaterMeasurementCollection,
    GroundwaterStation,
    GroundwaterStationCollection,
)

logger = logging.getLogger(__name__)

DATASET = "grundvattennivaer-observerade"


class ObservedGroundwaterLevelClient:
    """Client for observed groundwater level-related SGU API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize observed groundwater level client.

        Args:
            base_client: Base HTTP client instance
        """
        self._client = base_client
        self._stations = SGUCollection(
            base_client,
            dataset=DATASET,
            name="stationer",
            model=GroundwaterStationCollection,
            label="Station",
        )
        self._measurements = SGUCollection(
            base_client,
            dataset=DATASET,
            name="nivaer",
            model=GroundwaterMeasurementCollection,
            label="Measurement",
            date_field="obsdatum",
        )

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

        Example:

            >>> from sgu_client import SGUClient
            >>> with SGUClient() as client:
            ...     # get stations in southern Sweden
            ...     stations = client.levels.observed.get_stations(
            ...         bbox=[12.0, 55.0, 16.0, 58.0]
            ...     )
            ...     # filter stations by municipality using CQL
            ...     stations = client.levels.observed.get_stations(
            ...         filter_expr="kommun='Uppsala' AND akvifer='JS'"
            ...     )
        """
        return self._stations.query(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter_expr=filter_expr,
            sortby=sortby,
            **kwargs,
        )

    def get_station(self, station_id: str) -> GroundwaterStation:
        """Get a specific groundwater monitoring station by ID. This endpoint is provided by the OGC API
        but likely not used by any user.

        Args:
            station_id: Station identifier

        Returns:
            Typed groundwater monitoring station

        Raises:
            ValueError: If station not found or multiple stations returned
        """
        return self._stations.get(station_id)

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

        This method is used internally by convenience functions like
        ``get_measurements_by_name()`` by constructing filter expressions. A user
        may also do this, but readability is greater when using the built-in
        convenience functions.

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
        return self._measurements.query(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter_expr=filter_expr,
            sortby=sortby,
            **kwargs,
        )

    def get_measurement(self, measurement_id: str) -> GroundwaterMeasurement:
        """Get a specific groundwater level measurement by ID. This endpoint is provided by the OGGC API
        but likely not used by any user.

        Args:
            measurement_id: Measurement identifier

        Returns:
            Typed groundwater level measurement

        Raises:
            ValueError: If measurement not found or multiple measurements returned
        """
        return self._measurements.get(measurement_id)

    def get_station_by_name(
        self,
        station_id: str | None = None,
        station_name: str | None = None,
        **kwargs: Any,
    ) -> GroundwaterStation:
        """Convenience function to get a station by name ('station_id' or 'station_name').

        Args:
            station_id: Station identifier (maps to 'platsbeteckning' in API)
            station_name: Station name (maps to 'obsplatsnamn' in API)
            **kwargs: Additional query parameters (e.g., limit)

        Returns:
            Typed groundwater monitoring station

        Raises:
            ValueError: If neither parameter is provided, both are provided,
                       or if multiple stations are found

        Example:

            >>> from sgu_client import SGUClient
            >>> with SGUClient() as client:
            ...     # find station by platsbeteckning (recommended)
            ...     station = client.levels.observed.get_station_by_name(station_id="95_2")
            ...     # find station by obsplatsnamn
            ...     station = client.levels.observed.get_station_by_name(
            ...         station_name="Lagga_2"
            ...     )
            ...     print(station.properties.aquifer_description)
        """
        if station_id and station_name:
            raise ValueError(
                "Only one of 'station_id' or 'station_name' can be provided."
            )

        # Map English parameter names to Swedish API field names
        if station_id:
            name_type = "platsbeteckning"
            station = station_id
        elif station_name:
            name_type = "obsplatsnamn"
            station = station_name
        else:
            raise ValueError("Either 'station_id' or 'station_name' must be provided.")
        return self._stations.find_one(where={name_type: station}, **kwargs)

    def get_stations_by_names(
        self,
        station_id: list[str] | None = None,
        station_name: list[str] | None = None,
        **kwargs: Any,
    ) -> GroundwaterStationCollection:
        """Convenience function to get multiple stations by name ('station_id' or 'station_name').

        Args:
            station_id: List of station identifiers (maps to 'platsbeteckning' in API)
            station_name: List of station names (maps to 'obsplatsnamn' in API)
            **kwargs: Additional query parameters (e.g., limit)

        Returns:
            Typed collection of groundwater monitoring stations

        Raises:
            ValueError: If neither parameter is provided or both are provided

        Example:

            >>> from sgu_client import SGUClient
            >>> with SGUClient() as client:
            ...     # get multiple stations by their IDs
            ...     stations = client.levels.observed.get_stations_by_names(
            ...         station_id=["95_2", "101_1", "102_3"]
            ...     )
            ...     for station in stations.features:
            ...         print(f"{station.properties.station_id}: {station.properties.aquifer_code}")
        """
        if station_id and station_name:
            raise ValueError(
                "Only one of 'station_id' or 'station_name' can be provided."
            )

        # Map English parameter names to Swedish API field names
        if station_id:
            name_type = "platsbeteckning"
            stations = station_id
        elif station_name:
            name_type = "obsplatsnamn"
            stations = station_name
        else:
            raise ValueError("Either 'station_id' or 'station_name' must be provided.")
        return self._stations.query(where={name_type: stations}, **kwargs)

    def get_measurements_by_name(
        self,
        station_id: str | None = None,
        station_name: str | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> GroundwaterMeasurementCollection:
        """Get measurements for a specific station by name with optional time filtering.

        Args:
            station_id: Station identifier (maps to 'platsbeteckning' in API)
            station_name: Station name (maps to 'obsplatsnamn' in API)
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)
            limit: Maximum number of measurements to return
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater level measurements

        Raises:
            ValueError: If neither or both name parameters are provided,
                       or if station lookup fails

        Example:

            >>> from sgu_client import SGUClient
            >>> from datetime import datetime, timezone
            >>> with SGUClient() as client:
            ...     # get all measurements for a station
            ...     measurements = client.levels.observed.get_measurements_by_name(
            ...         station_id="95_2",
            ...         limit=100
            ...     )
            ...     # get measurements with time filtering
            ...     measurements = client.levels.observed.get_measurements_by_name(
            ...         station_id="95_2",
            ...         tmin=datetime(2020, 1, 1, tzinfo=timezone.utc),
            ...         tmax=datetime(2021, 1, 1, tzinfo=timezone.utc)
            ...     )
            ...     # using ISO string for time filtering
            ...     measurements = client.levels.observed.get_measurements_by_name(
            ...         station_id="95_2",
            ...         tmin="2020-01-01T00:00:00Z",
            ...         tmax="2021-01-01T00:00:00Z"
            ...     )
        """
        if station_id and station_name:
            raise ValueError(
                "Only one of 'station_id' or 'station_name' can be provided."
            )

        # If station_name provided, look up the station to get station_id
        if station_name:
            logger.warning(
                "Using 'station_name' requires an additional API request to lookup the station. "
                "For better performance, use 'station_id' directly if available."
            )
            # Don't pass kwargs to station lookup as it's a single result operation
            station = self.get_station_by_name(station_name=station_name)
            target_platsbeteckning = station.properties.station_id
            if not target_platsbeteckning:
                raise ValueError(
                    f"Station with station_name '{station_name}' has no station_id"
                )
        elif station_id:
            target_platsbeteckning = station_id
        else:
            raise ValueError("Either 'station_id' or 'station_name' must be provided.")

        return self._measurements.query(
            where={"platsbeteckning": target_platsbeteckning},
            tmin=tmin,
            tmax=tmax,
            limit=limit,
            **kwargs,
        )

    def get_measurements_by_names(
        self,
        station_id: list[str] | None = None,
        station_name: list[str] | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> GroundwaterMeasurementCollection:
        """Get measurements for multiple stations by name with optional time filtering.

        Args:
            station_id: List of station identifiers (maps to 'platsbeteckning' in API)
            station_name: List of station names (maps to 'obsplatsnamn' in API)
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)
            limit: Maximum number of measurements to return
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater level measurements

        Raises:
            ValueError: If neither or both name parameters are provided,
                       or if station lookup fails

        Example:

            >>> from sgu_client import SGUClient
            >>> with SGUClient() as client:
            ...     # get measurements for multiple stations
            ...     measurements = client.levels.observed.get_measurements_by_names(
            ...         station_id=["95_2", "101_1"],
            ...         tmin="2020-01-01T00:00:00Z",
            ...         tmax="2021-01-01T00:00:00Z",
            ...         limit=1000
            ...     )
            ...     print(f"Found {len(measurements.features)} measurements")
        """
        if station_id and station_name:
            raise ValueError(
                "Only one of 'station_id' or 'station_name' can be provided."
            )

        # If station_name provided, look up stations to get station_id values
        if station_name:
            logger.warning(
                "Using 'station_name' requires an additional API request to lookup stations. "
                "For better performance, use 'station_id' directly if available."
            )
            # Don't pass kwargs to station lookup as it's a separate operation
            stations = self.get_stations_by_names(station_name=station_name)
            target_platsbeteckningar = []
            for station in stations.features:
                if station.properties.station_id:
                    target_platsbeteckningar.append(station.properties.station_id)
                else:
                    raise ValueError(
                        f"Station {station.id} with station_name '{station.properties.station_name}' "
                        f"has no station_id"
                    )
        elif station_id:
            target_platsbeteckningar = station_id
        else:
            raise ValueError("Either 'station_id' or 'station_name' must be provided.")

        return self._measurements.query(
            where={"platsbeteckning": target_platsbeteckningar},
            tmin=tmin,
            tmax=tmax,
            limit=limit,
            **kwargs,
        )
