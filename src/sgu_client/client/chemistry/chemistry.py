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
    CHEMISTRY_BASE_URL = "https://api.sgu.se/oppnadata/grundvattenkvalitet-analysresultat-provplatser-v2/ogc/features/v1/"

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
        national_site_id: int | None = None,
        **kwargs: Any,
    ) -> SamplingSite:
        """Convenience function to get a sampling site by 'site_id', 'site_name' or 'national_site_id'.

        Args:
            site_id: Site identifier (maps to 'platsbeteckning' in API)
            site_name: Site name (maps to 'provplatsnamn' in API)
            national_site_id: National sampling site ID (maps to 'nationellt_provplatsid' in API)
            **kwargs: Additional query parameters (e.g., limit)

        Returns:
            Typed groundwater chemistry sampling site

        Raises:
            ValueError: If not exactly one identifier is provided,
                       or if no site or multiple sites are found

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # find site by id
            >>> site = client.chemistry.get_sampling_site_by_name(site_id="TTK-442-M")
            >>>
            >>> # find site by name
            >>> site = client.chemistry.get_sampling_site_by_name(site_name="Lena")
            >>>
            >>> # find site by national site id
            >>> site = client.chemistry.get_sampling_site_by_name(national_site_id=359366)
            >>> print(site.properties.municipality)
        """
        self._validate_site_identifiers(national_site_id, site_id, site_name)

        if national_site_id:
            filter_expr = f"nationellt_provplatsid={national_site_id}"
        elif site_id:
            filter_expr = f"platsbeteckning='{site_id}'"
        else:
            filter_expr = f"provplatsnamn='{site_name}'"

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
        national_site_id: list[int] | None = None,
        **kwargs: Any,
    ) -> SamplingSiteCollection:
        """Convenience function to get multiple sampling sites by 'site_id', 'site_name' or 'national_site_id'.

        Args:
            site_id: List of site identifiers (maps to 'platsbeteckning' in API)
            site_name: List of site names (maps to 'provplatsnamn' in API)
            national_site_id: List of national sampling site IDs (maps to 'nationellt_provplatsid' in API)
            **kwargs: Additional query parameters (e.g., limit)

        Returns:
            Typed collection of groundwater chemistry sampling sites

        Raises:
            ValueError: If not exactly one identifier is provided

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get multiple sampling sites by their IDs
            >>> sites = client.chemistry.get_sampling_sites_by_names(
            ...     site_id=["TTK-442-M", "SYD-681-C"]
            ... )
            >>> for site in sites.features:
            ...     print(f"{site.properties.station_id}: {site.properties.national_site_id}")
        """
        self._validate_site_identifiers(national_site_id, site_id, site_name)

        if national_site_id:
            name_type = "nationellt_provplatsid"
            values = [str(site) for site in national_site_id]
        else:
            name_type = "platsbeteckning" if site_id else "provplatsnamn"
            # sites is guaranteed to not be None by the validation above
            values = [f"'{site}'" for site in site_id or site_name]  # type: ignore[union-attr]

        filter_expr = f"{name_type} in ({', '.join(values)})"

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
        national_site_id: int | None = None,
        site_id: str | None = None,
        site_name: str | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> AnalysisResultCollection:
        """Get analysis results for a specific site with optional time filtering.

        Analysis results are linked to sampling sites by `national_site_id`, which is
        the recommended (and fastest) way to identify a site. Using `site_id` or
        `site_name` requires an additional API request to look up the site.

        Args:
            national_site_id: National sampling site ID (maps to 'nationellt_provplatsid' in API)
            site_id: Site identifier (maps to 'platsbeteckning' in API)
            site_name: Site name (maps to 'provplatsnamn' in API)
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)
            limit: Maximum number of results to return
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater chemistry analysis results

        Raises:
            ValueError: If not exactly one site identifier is provided,
                       or if site lookup fails

        Example:

            >>> from sgu_client import SGUClient
            >>> from datetime import datetime, timezone
            >>> client = SGUClient()
            >>>
            >>> # get all results for a site
            >>> results = client.chemistry.get_results_by_site(359366, limit=100)
            >>>
            >>> # get results with time filtering
            >>> results = client.chemistry.get_results_by_site(
            ...     359366,
            ...     tmin=datetime(2020, 1, 1, tzinfo=timezone.utc),
            ...     tmax=datetime(2021, 1, 1, tzinfo=timezone.utc)
            ... )
        """
        self._validate_site_identifiers(national_site_id, site_id, site_name)

        if national_site_id:
            national_site_ids = [national_site_id]
        else:
            national_site_ids = self._lookup_national_site_ids(
                site_id=[site_id] if site_id else None,
                site_name=[site_name] if site_name else None,
            )
            if len(national_site_ids) > 1:
                raise ValueError(
                    f"Multiple sites found for {self._describe(site_id, site_name)}"
                )

        filters = [self._build_national_site_filter(national_site_ids)]
        filters.extend(self._build_datetime_filters(tmin, tmax))

        return self.get_analysis_results(
            filter_expr=" AND ".join(filters),
            limit=limit,
            **kwargs,
        )

    def get_results_by_sites(
        self,
        national_site_id: list[int] | None = None,
        site_id: list[str] | None = None,
        site_name: list[str] | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> AnalysisResultCollection:
        """Get analysis results for multiple sites with optional time filtering.

        Analysis results are linked to sampling sites by `national_site_id`, which is
        the recommended (and fastest) way to identify sites. Using `site_id` or
        `site_name` requires an additional API request to look up the sites.

        Args:
            national_site_id: List of national sampling site IDs (maps to 'nationellt_provplatsid' in API)
            site_id: List of site identifiers (maps to 'platsbeteckning' in API)
            site_name: List of site names (maps to 'provplatsnamn' in API)
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)
            limit: Maximum number of results to return
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater chemistry analysis results

        Raises:
            ValueError: If not exactly one site identifier is provided,
                       or if any site is not found in the lookup

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get results for multiple sites
            >>> results = client.chemistry.get_results_by_sites(
            ...     [359366, 378865],
            ...     tmin="2020-01-01T00:00:00Z",
            ...     tmax="2021-01-01T00:00:00Z",
            ...     limit=1000
            ... )
            >>> print(f"Found {len(results.features)} analysis results")
        """
        self._validate_site_identifiers(national_site_id, site_id, site_name)

        if national_site_id:
            national_site_ids = national_site_id
        else:
            national_site_ids = self._lookup_national_site_ids(
                site_id=site_id, site_name=site_name
            )

        filters = [self._build_national_site_filter(national_site_ids)]
        filters.extend(self._build_datetime_filters(tmin, tmax))

        return self.get_analysis_results(
            filter_expr=" AND ".join(filters),
            limit=limit,
            **kwargs,
        )

    def get_results_by_parameter(
        self,
        parameter: str,
        national_site_id: int | list[int] | None = None,
        site_id: str | list[str] | None = None,
        site_name: str | list[str] | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> AnalysisResultCollection:
        """Get analysis results filtered by chemical parameter (e.g., pH, nitrate).

        This convenience method makes it easy to retrieve all measurements for a specific
        chemical parameter, optionally filtered by site(s) and time range. Sites are
        identified the same way as in `get_results_by_site()`: `national_site_id` is
        recommended, while `site_id` or `site_name` require an additional API request.

        Args:
            parameter: Parameter name as used by SGU (maps to 'parameternamn' in API),
                e.g. 'pH', 'Bly', 'Nitratkväve', 'Klorid'
            national_site_id: Optional national sampling site ID(s) to filter by
            site_id: Optional site identifier(s) to filter by
            site_name: Optional site name(s) to filter by
            tmin: Start time (ISO string or datetime object)
            tmax: End time (ISO string or datetime object)
            limit: Maximum number of results to return
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater chemistry analysis results

        Raises:
            ValueError: If more than one site identifier is provided,
                       or if any site is not found in the lookup

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get all lead measurements since 2020
            >>> results = client.chemistry.get_results_by_parameter(
            ...     parameter="Bly",
            ...     tmin="2020-01-01",
            ... )
            >>>
            >>> # get pH measurements for a specific site
            >>> results = client.chemistry.get_results_by_parameter(
            ...     parameter="pH",
            ...     national_site_id=359366,
            ...     tmin="2020-01-01",
            ...     tmax="2021-01-01"
            ... )
            >>>
            >>> # ... or multiple sites
            >>> results = client.chemistry.get_results_by_parameter(
            ...     parameter="pH",
            ...     national_site_id=[359366, 378865]
            ... )
        """
        filters = [f"parameternamn='{parameter}'"]

        if national_site_id or site_id or site_name:
            self._validate_site_identifiers(national_site_id, site_id, site_name)
            if national_site_id:
                national_site_ids = self._as_list(national_site_id)
            else:
                national_site_ids = self._lookup_national_site_ids(
                    site_id=self._as_list(site_id) if site_id else None,
                    site_name=self._as_list(site_name) if site_name else None,
                )
            filters.append(self._build_national_site_filter(national_site_ids))

        filters.extend(self._build_datetime_filters(tmin, tmax))

        return self.get_analysis_results(
            filter_expr=" AND ".join(filters),
            limit=limit,
            **kwargs,
        )

    # ===== Internal Helper Methods =====

    def _validate_site_identifiers(
        self,
        national_site_id: Any,
        site_id: Any,
        site_name: Any,
    ) -> None:
        """Ensure exactly one site identifier is provided.

        Raises:
            ValueError: If none or more than one identifier is provided
        """
        provided = [
            identifier
            for identifier in (national_site_id, site_id, site_name)
            if identifier
        ]
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'national_site_id', 'site_id' or 'site_name' "
                "must be provided."
            )

    def _lookup_national_site_ids(
        self,
        site_id: list[str] | None = None,
        site_name: list[str] | None = None,
    ) -> list[int]:
        """Look up the national site IDs of sampling sites by `site_id` or `site_name`.

        Analysis results only reference sampling sites by national site ID, so this
        costs one additional API request.

        Raises:
            ValueError: If any of the requested sites is not found
        """
        identifier = "site_id" if site_id else "site_name"
        logger.warning(
            f"Using '{identifier}' requires an additional API request to look up "
            "the sampling site(s). For better performance, use 'national_site_id' "
            "directly if available."
        )
        sites = self.get_sampling_sites_by_names(site_id=site_id, site_name=site_name)

        requested = site_id or site_name or []
        if site_id:
            found = {site.properties.station_id for site in sites.features}
        else:
            found = {site.properties.site_name for site in sites.features}
        missing = [value for value in requested if value not in found]
        if missing:
            raise ValueError(f"No sampling sites found for {identifier}: {missing}")

        return [
            site.properties.national_site_id
            for site in sites.features
            if site.properties.national_site_id is not None
        ]

    def _build_national_site_filter(self, national_site_ids: list[int]) -> str:
        """Build a CQL filter matching analysis results for the given sites."""
        if len(national_site_ids) == 1:
            return f"nationellt_provplatsid={national_site_ids[0]}"
        return f"nationellt_provplatsid in ({', '.join(map(str, national_site_ids))})"

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        """Wrap a single value in a list, leaving lists untouched."""
        return value if isinstance(value, list) else [value]

    @staticmethod
    def _describe(site_id: str | None, site_name: str | None) -> str:
        """Describe a site identifier for error messages."""
        return f"site_id '{site_id}'" if site_id else f"site_name '{site_name}'"

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
            filters.append(f"provtagningsdatum >= '{tmin_str}'")

        if tmax:
            tmax_str = to_iso_string(tmax)
            filters.append(f"provtagningsdatum <= '{tmax_str}'")

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
