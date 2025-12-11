"""Groundwater chemistry client endpoints."""

import logging
from datetime import datetime
from typing import Any

from sgu_client.client.base import BaseClient
from sgu_client.models.chemistry import (
    AnalysisResult,
    AnalysisResultCollection,
    SamplingSite,
    SamplingSiteCollection,
)

logger = logging.getLogger(__name__)


class GroundwaterChemistryClient:
    """Client for groundwater chemistry-related SGU API endpoints."""

    BASE_PATH = "collections"
    CHEMISTRY_BASE_URL = "https://api.sgu.se/oppnadata/grundvattenkvalitet-analysresultat-provplatser/ogc/features/v1/"

    def __init__(self, base_client: BaseClient):
        """Initialize groundwater chemistry client.

        Args:
            base_client: Base HTTP client instance
        """
        self._client = base_client

    # ===== Sampling Sites Methods =====

    def get_sampling_sites(
        self,
        bbox: list[float] | None = None,
        datetime: str | None = None,
        limit: int | None = None,
        filter_expr: str | None = None,
        sortby: list[str] | None = None,
        **kwargs: Any,
    ) -> SamplingSiteCollection:
        """Get groundwater chemistry sampling sites. This method is used internally by convenience functions like
        `get_sampling_site_by_name() by constructing filter expressions. A user may also do this, but readability
        is greater when using the built-in convenience functions.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            datetime: Date/time filter (RFC 3339 format or interval)
            limit: Maximum number of features to return (automatically paginated if needed)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+name', '-date'])
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater chemistry sampling sites
        """
        endpoint = f"{self.BASE_PATH}/provplatser/items"
        params = self._build_query_params(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter=filter_expr,
            sortby=sortby,
            **kwargs,
        )
        response = self._make_request(endpoint, params)
        return SamplingSiteCollection(**response)

    def get_sampling_site(self, site_id: str) -> SamplingSite:
        """Get a specific groundwater chemistry sampling site by ID. This endpoint is provided by the OGC API
        but likely not used by any user.

        Args:
            site_id: Site identifier

        Returns:
            Typed groundwater chemistry sampling site

        Raises:
            ValueError: If site not found or multiple sites returned
        """
        endpoint = f"{self.BASE_PATH}/provplatser/items/{site_id}"
        response = self._make_request(endpoint, {})

        # SGU API returns a FeatureCollection even for single items
        collection = SamplingSiteCollection(**response)
        if not collection.features:
            raise ValueError(f"Site {site_id} not found")
        if len(collection.features) > 1:
            raise ValueError(f"Multiple sites returned for ID {site_id}")

        return collection.features[0]

    def get_sampling_site_by_name(
        self,
        site_id: str | None = None,
        site_name: str | None = None,
        **kwargs: Any,
    ) -> SamplingSite:
        """Convenience function to get a sampling site by name ('site_id' or 'site_name').

        Args:
            site_id: Site identifier (maps to 'platsbeteckning' in API)
            site_name: Site name (maps to 'provplatsnamn' in API)
            **kwargs: Additional query parameters (e.g., limit)

        Returns:
            Typed groundwater chemistry sampling site

        Raises:
            ValueError: If neither parameter is provided, both are provided,
                       or if multiple sites are found

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # find site by id
            >>> site = client.chemistry.get_sampling_site_by_name(site_id="10001_1")
            >>>
            >>> # find site by name
            >>> site = client.chemistry.get_sampling_site_by_name(
            ...     site_name="Ringarum_1"
            ... )
            >>> print(site.properties.municipality)
        """
        if not site_id and not site_name:
            raise ValueError("Either 'site_id' or 'site_name' must be provided.")
        if site_id and site_name:
            raise ValueError("Only one of 'site_id' or 'site_name' can be provided.")

        # Map English parameter names to Swedish API field names
        if site_id:
            name_type = "platsbeteckning"
            site = site_id
        else:
            name_type = "provplatsnamn"
            site = site_name

        filter_expr = f"{name_type}='{site}'"
        response = self.get_sampling_sites(filter_expr=filter_expr, **kwargs)

        if not response.features:
            raise ValueError(f"No sites found for {filter_expr}")
        if len(response.features) > 1:
            raise ValueError(f"Multiple sites found for {filter_expr}")

        return response.features[0]

    def get_sampling_sites_by_names(
        self,
        site_id: list[str] | None = None,
        site_name: list[str] | None = None,
        **kwargs: Any,
    ) -> SamplingSiteCollection:
        """Convenience function to get multiple sampling sites by name ('site_id' or 'site_name').

        Args:
            site_id: List of site identifiers (maps to 'platsbeteckning' in API)
            site_name: List of site names (maps to 'provplatsnamn' in API)
            **kwargs: Additional query parameters (e.g., limit)

        Returns:
            Typed collection of groundwater chemistry sampling sites

        Raises:
            ValueError: If neither parameter is provided or both are provided

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get multiple sampling sites by their IDs
            >>> sites = client.chemistry.get_sampling_sites_by_names(
            ...     site_id=["10001_1", "10002_1", "10003_1"]
            ... )
            >>> for site in sites.features:
            ...     print(f"{site.properties.station_id}: {site.properties.municipality}")
        """
        if not site_id and not site_name:
            raise ValueError("Either 'site_id' or 'site_name' must be provided.")
        if site_id and site_name:
            raise ValueError("Only one of 'site_id' or 'site_name' can be provided.")

        # Map English parameter names to Swedish API field names
        if site_id:
            name_type = "platsbeteckning"
            sites = site_id
        else:
            name_type = "provplatsnamn"
            sites = site_name

        # Build filter expression for multiple sites using IN clause
        # sites is guaranteed to not be None by the validation above
        quoted_sites = [f"'{site}'" for site in sites]  # type: ignore[union-attr]
        filter_expr = f"{name_type} in ({', '.join(quoted_sites)})"

        return self.get_sampling_sites(filter_expr=filter_expr, **kwargs)

    # ===== Analysis Results Methods =====

    def get_analysis_results(
        self,
        bbox: list[float] | None = None,
        datetime: str | None = None,
        limit: int | None = None,
        filter_expr: str | None = None,
        sortby: list[str] | None = None,
        **kwargs: Any,
    ) -> AnalysisResultCollection:
        """Get groundwater chemistry analysis results. This method is used internally by convenience functions like
        `get_results_by_site() by constructing filter expressions. A user may also do this, but readability
        is greater when using the built-in convenience functions.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            datetime: Date/time filter (RFC 3339 format or interval)
            limit: Maximum number of features to return (automatically paginated if needed)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+date', '-value'])
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater chemistry analysis results
        """
        endpoint = f"{self.BASE_PATH}/analysresultat/items"
        params = self._build_query_params(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter=filter_expr,
            sortby=sortby,
            **kwargs,
        )
        response = self._make_request(endpoint, params)
        return AnalysisResultCollection(**response)

    def get_analysis_result(self, result_id: str) -> AnalysisResult:
        """Get a specific groundwater chemistry analysis result by ID. This endpoint is provided by the OGC API
        but likely not used by any user.

        Args:
            result_id: Result identifier

        Returns:
            Typed groundwater chemistry analysis result

        Raises:
            ValueError: If result not found or multiple results returned
        """
        endpoint = f"{self.BASE_PATH}/analysresultat/items/{result_id}"
        response = self._make_request(endpoint, {})

        # SGU API returns a FeatureCollection even for single items
        collection = AnalysisResultCollection(**response)
        if not collection.features:
            raise ValueError(f"Result {result_id} not found")
        if len(collection.features) > 1:
            raise ValueError(f"Multiple results returned for ID {result_id}")

        return collection.features[0]

    def get_results_by_site(
        self,
        site_id: str | None = None,
        site_name: str | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> AnalysisResultCollection:
        """Get analysis results for a specific site by name with optional time filtering.

        Args:
            site_id: Site identifier (maps to 'platsbeteckning' in API)
            site_name: Site name (maps to 'provplatsnamn' in API)
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)
            limit: Maximum number of results to return
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater chemistry analysis results

        Raises:
            ValueError: If neither or both name parameters are provided,
                       or if site lookup fails

        Example:

            >>> from sgu_client import SGUClient
            >>> from datetime import datetime, timezone
            >>> client = SGUClient()
            >>>
            >>> # get all results for a site
            >>> results = client.chemistry.get_results_by_site(
            ...     site_id="10001_1",
            ...     limit=100
            ... )
            >>>
            >>> # get results with time filtering
            >>> results = client.chemistry.get_results_by_site(
            ...     site_id="10001_1",
            ...     tmin=datetime(2020, 1, 1, tzinfo=timezone.utc),
            ...     tmax=datetime(2021, 1, 1, tzinfo=timezone.utc)
            ... )
        """
        if not site_id and not site_name:
            raise ValueError("Either 'site_id' or 'site_name' must be provided.")
        if site_id and site_name:
            raise ValueError("Only one of 'site_id' or 'site_name' can be provided.")

        # If site_name provided, look up the site to get station_id
        if site_name:
            logger.warning(
                "Using 'site_name' requires an additional API request to lookup the site. "
                "For better performance, use 'station_id' directly if available."
            )
            # Don't pass kwargs to site lookup as it's a single result operation
            site = self.get_sampling_site_by_name(site_name=site_name)
            target_platsbeteckning = site.properties.station_id
            if not target_platsbeteckning:
                raise ValueError(f"Site with site_name '{site_name}' has no station_id")
        else:
            target_platsbeteckning = site_id

        # Build filter expressions
        filters = [f"platsbeteckning='{target_platsbeteckning}'"]

        # Add datetime filters if tmin/tmax provided
        datetime_filters = self._build_datetime_filters(tmin, tmax)
        filters.extend(datetime_filters)

        # Combine all filters with AND
        combined_filter = " AND ".join(filters)

        return self.get_analysis_results(
            filter_expr=combined_filter,
            limit=limit,
            **kwargs,
        )

    def get_results_by_sites(
        self,
        site_id: list[str] | None = None,
        site_name: list[str] | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> AnalysisResultCollection:
        """Get analysis results for multiple sites by name with optional time filtering.

        Args:
            site_id: List of station identifiers (maps to 'platsbeteckning' in API)
            site_name: List of site names (maps to 'provplatsnamn' in API)
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)
            limit: Maximum number of results to return
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater chemistry analysis results

        Raises:
            ValueError: If neither or both name parameters are provided,
                       or if site lookup fails

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get results for multiple sites
            >>> results = client.chemistry.get_results_by_sites(
            ...     station_id=["10001_1", "10002_1"],
            ...     tmin="2020-01-01T00:00:00Z",
            ...     tmax="2021-01-01T00:00:00Z",
            ...     limit=1000
            ... )
            >>> print(f"Found {len(results.features)} analysis results")
        """
        if not site_id and not site_name:
            raise ValueError("Either 'site_id' or 'site_name' must be provided.")
        if site_id and site_name:
            raise ValueError("Only one of 'site_id' or 'site_name' can be provided.")

        # If site_name provided, look up sites to get station_id values
        if site_name:
            logger.warning(
                "Using 'site_name' requires an additional API request to lookup sites. "
                "For better performance, use 'station_id' directly if available."
            )
            # Don't pass kwargs to site lookup as it's a separate operation
            sites = self.get_sampling_sites_by_names(site_name=site_name)
            target_platsbeteckningar = []
            for site in sites.features:
                if site.properties.station_id:
                    target_platsbeteckningar.append(site.properties.station_id)
                else:
                    raise ValueError(
                        f"Site {site.id} with site_name '{site.properties.site_name}' "
                        f"has no station_id"
                    )
        else:
            target_platsbeteckningar = site_id

        # Build filter expressions
        # target_platsbeteckningar is guaranteed to not be None by validation above
        quoted_sites = [f"'{site}'" for site in target_platsbeteckningar]  # type: ignore[union-attr]
        filters = [f"platsbeteckning in ({', '.join(quoted_sites)})"]

        # Add datetime filters if tmin/tmax provided
        datetime_filters = self._build_datetime_filters(tmin, tmax)
        filters.extend(datetime_filters)

        # Combine all filters with AND
        combined_filter = " AND ".join(filters)

        return self.get_analysis_results(
            filter_expr=combined_filter,
            limit=limit,
            **kwargs,
        )

    def get_results_by_parameter(
        self,
        parameter: str,
        site_id: str | list[str] | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> AnalysisResultCollection:
        """Get analysis results filtered by chemical parameter (e.g., pH, nitrate).

        This convenience method makes it easy to retrieve all measurements for a specific
        chemical parameter, optionally filtered by site and time range.

        Args:
            parameter: Parameter short name (e.g., 'PH', 'NITRATE', 'KLORID')
            site_id: Optional station identifier(s) to filter by
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)
            limit: Maximum number of results to return
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater chemistry analysis results

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get all pH measurements
            >>> results = client.chemistry.get_results_by_parameter(
            ...     parameter="PH",
            ...     limit=1000
            ... )
            >>>
            >>> # get pH measurements for a specific site
            >>> results = client.chemistry.get_results_by_parameter(
            ...     parameter="PH",
            ...     site_id="10001_1",
            ...     tmin="2020-01-01",
            ...     tmax="2021-01-01"
            ... )
            >>>
            >>> # ... or multiple sites
            >>> results = client.chemistry.get_results_by_parameter(
            ...     parameter="PH",
            ...     site_id=["10001_1", "10002_1"]
            ... )
        """
        # Build filter expressions
        filters = [f"param_kort='{parameter}'"]

        # Add station filter if provided
        if site_id:
            if isinstance(site_id, list):
                quoted_sites = [f"'{site}'" for site in site_id]
                filters.append(f"platsbeteckning in ({', '.join(quoted_sites)})")
            else:
                filters.append(f"platsbeteckning='{site_id}'")

        # Add datetime filters if tmin/tmax provided
        datetime_filters = self._build_datetime_filters(tmin, tmax)
        filters.extend(datetime_filters)

        # Combine all filters with AND
        combined_filter = " AND ".join(filters)

        return self.get_analysis_results(
            filter_expr=combined_filter,
            limit=limit,
            **kwargs,
        )

    # ===== Internal Helper Methods =====

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
            filters.append(f"provtagningsdat >= '{tmin_str}'")

        if tmax:
            tmax_str = to_iso_string(tmax)
            filters.append(f"provtagningsdat <= '{tmax_str}'")

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
        return self._client.get(
            endpoint, params=params, base_url=self.CHEMISTRY_BASE_URL
        )
