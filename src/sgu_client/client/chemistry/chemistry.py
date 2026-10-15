"""Groundwater chemistry client endpoints."""

import logging
from collections.abc import Sequence
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

# A single site identifier value, or a list of them
SiteIdentifier = int | str | list[int] | list[str] | None

# Site identifier argument -> (API field, SamplingSiteProperties attribute)
SITE_IDENTIFIERS: dict[str, tuple[str, str]] = {
    "national_site_id": ("nationellt_provplatsid", "national_site_id"),
    "site_id": ("platsbeteckning", "station_id"),
    "site_name": ("provplatsnamn", "site_name"),
}


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
        """Get groundwater chemistry sampling sites.

        This method is used internally by convenience functions like
        `get_sampling_site_by_name()` by constructing filter expressions. A user may
        also do this, but readability is greater when using the built-in convenience
        functions.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            datetime: Date/time filter (RFC 3339 format or interval)
            limit: Maximum number of features to return (paginated automatically)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+name', '-date'])
                Note: the SGU v2 chemistry API currently ignores sortby;
                features are returned in the server's default order.
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
        """Get a specific groundwater chemistry sampling site by ID.

        This endpoint is provided by the OGC API but likely not used by any user.

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
        """Convenience function to get a sampling site by any site identifier.

        Args:
            site_id: Site identifier (maps to 'platsbeteckning' in API)
            site_name: Site name (maps to 'provplatsnamn' in API)
            national_site_id: National sampling site ID
                (maps to 'nationellt_provplatsid' in API)
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
            >>> site = client.chemistry.get_sampling_site_by_name(
            ...     national_site_id=359366
            ... )
            >>> print(site.properties.municipality)
        """
        identifier, values = self._select_site_identifier(
            national_site_id, site_id, site_name
        )
        filter_expr = self._build_site_filter(identifier, values)
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
        """Convenience function to get multiple sampling sites by any site identifier.

        Args:
            site_id: List of site identifiers (maps to 'platsbeteckning' in API)
            site_name: List of site names (maps to 'provplatsnamn' in API)
            national_site_id: List of national sampling site IDs
                (maps to 'nationellt_provplatsid' in API)
            **kwargs: Additional query parameters (e.g., limit)

        Returns:
            Typed collection of groundwater chemistry sampling sites

        Raises:
            ValueError: If not exactly one identifier is provided,
                       or if any of the requested sites is not found

        Example:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> # get multiple sampling sites by their IDs
            >>> sites = client.chemistry.get_sampling_sites_by_names(
            ...     site_id=["TTK-442-M", "SYD-681-C"]
            ... )
            >>> for site in sites.features:
            ...     props = site.properties
            ...     print(f"{props.station_id}: {props.national_site_id}")
        """
        identifier, values = self._select_site_identifier(
            national_site_id, site_id, site_name
        )
        return self._get_all_sampling_sites(identifier, values, **kwargs)

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
        """Get groundwater chemistry analysis results.

        This method is used internally by convenience functions like
        `get_results_by_site()` by constructing filter expressions. A user may also
        do this, but readability is greater when using the built-in convenience
        functions.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            datetime: Date/time filter (RFC 3339 format or interval)
            limit: Maximum number of features to return (paginated automatically)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+date', '-value'])
                Note: the SGU v2 chemistry API currently ignores sortby;
                features are returned in the server's default order.
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
        """Get a specific groundwater chemistry analysis result by ID.

        This endpoint is provided by the OGC API but likely not used by any user.

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
            national_site_id: National sampling site ID
                (maps to 'nationellt_provplatsid' in API)
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
        national_site_ids = self._resolve_national_site_ids(
            national_site_id, site_id, site_name
        )
        if len(national_site_ids) > 1:
            raise ValueError(f"Multiple sites found for {site_id or site_name!r}")

        return self._get_results_for_filters(
            [self._build_site_filter("national_site_id", national_site_ids)],
            tmin=tmin,
            tmax=tmax,
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
            national_site_id: List of national sampling site IDs
                (maps to 'nationellt_provplatsid' in API)
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
        national_site_ids = self._resolve_national_site_ids(
            national_site_id, site_id, site_name
        )

        return self._get_results_for_filters(
            [self._build_site_filter("national_site_id", national_site_ids)],
            tmin=tmin,
            tmax=tmax,
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

        This convenience method makes it easy to retrieve all measurements for a
        specific chemical parameter, optionally filtered by site(s) and time range.
        Sites are identified the same way as in `get_results_by_site()`:
        `national_site_id` is recommended, while `site_id` or `site_name` require an
        additional API request.

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
            national_site_ids = self._resolve_national_site_ids(
                national_site_id, site_id, site_name
            )
            filters.append(
                self._build_site_filter("national_site_id", national_site_ids)
            )

        return self._get_results_for_filters(
            filters, tmin=tmin, tmax=tmax, limit=limit, **kwargs
        )

    # ===== Internal Helper Methods =====

    def _select_site_identifier(
        self,
        national_site_id: SiteIdentifier,
        site_id: SiteIdentifier,
        site_name: SiteIdentifier,
    ) -> tuple[str, list[int | str]]:
        """Pick the single site identifier provided and return its values as a list.

        Returns:
            Tuple of the identifier argument name and its value(s) as a list

        Raises:
            ValueError: If none or more than one identifier is provided
        """
        provided = {
            identifier: value
            for identifier, value in (
                ("national_site_id", national_site_id),
                ("site_id", site_id),
                ("site_name", site_name),
            )
            if value
        }
        if len(provided) != 1:
            raise ValueError(
                "Exactly one of 'national_site_id', 'site_id' or 'site_name' "
                "must be provided."
            )
        ((identifier, value),) = provided.items()
        return identifier, list(value) if isinstance(value, list) else [value]

    def _resolve_national_site_ids(
        self,
        national_site_id: SiteIdentifier,
        site_id: SiteIdentifier,
        site_name: SiteIdentifier,
    ) -> list[int]:
        """Resolve any site identifier to the national site IDs results reference.

        Analysis results only reference sampling sites by national site ID, so
        `site_id` or `site_name` cost one additional API request to look up.

        Raises:
            ValueError: If not exactly one identifier is provided, if any site is
                not found, or if a site has no national site ID
        """
        identifier, values = self._select_site_identifier(
            national_site_id, site_id, site_name
        )
        if identifier == "national_site_id":
            return [int(value) for value in values]

        logger.warning(
            f"Using '{identifier}' requires an additional API request to look up "
            "the sampling site(s). For better performance, use 'national_site_id' "
            "directly if available."
        )
        sites = self._get_all_sampling_sites(identifier, values)

        national_site_ids = []
        for site in sites.features:
            if site.properties.national_site_id is None:
                raise ValueError(f"Sampling site {site.id} has no national_site_id")
            national_site_ids.append(site.properties.national_site_id)
        return national_site_ids

    def _get_all_sampling_sites(
        self, identifier: str, values: list[int | str], **kwargs: Any
    ) -> SamplingSiteCollection:
        """Get the sampling sites matching the identifier values, requiring all of them.

        Raises:
            ValueError: If any of the requested sites is not found
        """
        sites = self.get_sampling_sites(
            filter_expr=self._build_site_filter(identifier, values), **kwargs
        )

        _, attribute = SITE_IDENTIFIERS[identifier]
        found = {getattr(site.properties, attribute) for site in sites.features}
        missing = [value for value in values if value not in found]
        if missing:
            raise ValueError(f"No sampling sites found for {identifier}: {missing}")

        return sites

    def _build_site_filter(self, identifier: str, values: Sequence[int | str]) -> str:
        """Build a CQL filter matching any of the given site identifier values."""
        field, _ = SITE_IDENTIFIERS[identifier]
        literals = [
            f"'{value}'" if isinstance(value, str) else str(value) for value in values
        ]
        if len(literals) == 1:
            return f"{field}={literals[0]}"
        return f"{field} in ({', '.join(literals)})"

    def _get_results_for_filters(
        self,
        filters: list[str],
        tmin: str | datetime | None,
        tmax: str | datetime | None,
        limit: int | None,
        **kwargs: Any,
    ) -> AnalysisResultCollection:
        """Get analysis results matching all filters and the optional time range."""
        filters = [*filters, *self._build_datetime_filters(tmin, tmax)]
        return self.get_analysis_results(
            filter_expr=" AND ".join(filters), limit=limit, **kwargs
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
