"""Groundwater chemistry client endpoints."""

from datetime import datetime
from typing import Any

from sgu_client.client.base import BaseClient
from sgu_client.client.collection import SGUCollection, Where
from sgu_client.client.identifiers import IdentifierLookup
from sgu_client.models.chemistry import (
    AnalysisResult,
    AnalysisResultCollection,
    SamplingSite,
    SamplingSiteCollection,
)

DATASET = "grundvattenkvalitet-analysresultat-provplatser-v2"

# Site identifier argument -> (API field, SamplingSiteProperties attribute)
SITE_IDENTIFIERS: dict[str, tuple[str, str]] = {
    "national_site_id": ("nationellt_provplatsid", "national_site_id"),
    "site_id": ("platsbeteckning", "station_id"),
    "site_name": ("provplatsnamn", "site_name"),
}

# The field analysis results refer to their sampling site by
RESULT_SITE_FIELD = "nationellt_provplatsid"


class GroundwaterChemistryClient:
    """Client for groundwater chemistry-related SGU API endpoints."""

    def __init__(self, base_client: BaseClient):
        """Initialize groundwater chemistry client.

        Args:
            base_client: Base HTTP client instance
        """
        self._client = base_client
        self._sites = SGUCollection(
            base_client,
            dataset=DATASET,
            name="provplatser",
            model=SamplingSiteCollection,
            label="Site",
        )
        self._results = SGUCollection(
            base_client,
            dataset=DATASET,
            name="analysresultat",
            model=AnalysisResultCollection,
            label="Result",
            date_field="provtagningsdatum",
        )
        self._site_lookup = IdentifierLookup(
            self._sites, SITE_IDENTIFIERS, key="national_site_id", noun="sampling site"
        )

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
        return self._sites.query(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter_expr=filter_expr,
            sortby=sortby,
            **kwargs,
        )

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
        return self._sites.get(site_id)

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
            SGUNotFoundError: If no site matches.
            SGUAmbiguousError: If several sites match.
            ValueError: If not exactly one identifier is provided.

        Example:

            >>> from sgu_client import SGUClient
            >>> with SGUClient() as client:
            ...     # find site by id
            ...     site = client.chemistry.get_sampling_site_by_name(site_id="TTK-442-M")
            ...     # find site by name
            ...     site = client.chemistry.get_sampling_site_by_name(site_name="Lena")
            ...     # find site by national site id
            ...     site = client.chemistry.get_sampling_site_by_name(
            ...         national_site_id=359366
            ...     )
            ...     print(site.properties.municipality)
        """
        return self._site_lookup.find_one(
            {
                "national_site_id": national_site_id,
                "site_id": site_id,
                "site_name": site_name,
            },
            **kwargs,
        )

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
            SGUNotFoundError: If any of the requested sites is not found.
            ValueError: If not exactly one identifier is provided.

        Example:

            >>> from sgu_client import SGUClient
            >>> with SGUClient() as client:
            ...     # get multiple sampling sites by their IDs
            ...     sites = client.chemistry.get_sampling_sites_by_names(
            ...         site_id=["TTK-442-M", "SYD-681-C"]
            ...     )
            ...     for site in sites.features:
            ...         props = site.properties
            ...         print(f"{props.station_id}: {props.national_site_id}")
        """
        return self._site_lookup.find_all(
            {
                "national_site_id": national_site_id,
                "site_id": site_id,
                "site_name": site_name,
            },
            **kwargs,
        )

    # ===== Analysis Results Methods =====

    def get_analysis_results(
        self,
        bbox: list[float] | None = None,
        datetime: str | None = None,
        limit: int | None = None,
        filter_expr: str | None = None,
        sortby: list[str] | None = None,
        tmin: str | datetime | None = None,
        tmax: str | datetime | None = None,
        **kwargs: Any,
    ) -> AnalysisResultCollection:
        """Get groundwater chemistry analysis results.

        This method is used internally by convenience functions like
        `get_results_by_site()` by constructing filter expressions. A user may also
        do this, but readability is greater when using the built-in convenience
        functions.

        Args:
            bbox: Bounding box as [min_lon, min_lat, max_lon, max_lat]
            datetime: Raw OGC date/time filter; prefer ``tmin``/``tmax``
            limit: Maximum number of features to return (paginated automatically)
            filter_expr: CQL filter expression
            sortby: List of sort expressions (e.g., ['+date', '-value'])
                Note: the SGU v2 chemistry API currently ignores sortby;
                features are returned in the server's default order.
            tmin: Earliest sampling date (ISO string or datetime object)
            tmax: Latest sampling date (ISO string or datetime object)
            **kwargs: Additional query parameters

        Returns:
            Typed collection of groundwater chemistry analysis results
        """
        return self._results.query(
            bbox=bbox,
            datetime=datetime,
            limit=limit,
            filter_expr=filter_expr,
            sortby=sortby,
            tmin=tmin,
            tmax=tmax,
            **kwargs,
        )

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
        return self._results.get(result_id)

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
            SGUNotFoundError: If a site_id or site_name matches no site.
            SGUAmbiguousError: If a site_id or site_name matches several sites.
            ValueError: If not exactly one site identifier is provided, or if the
                looked-up site has no national_site_id.

        Example:

            >>> from sgu_client import SGUClient
            >>> from datetime import datetime, timezone
            >>> with SGUClient() as client:
            ...     # get all results for a site
            ...     results = client.chemistry.get_results_by_site(359366, limit=100)
            ...     # get results with time filtering
            ...     results = client.chemistry.get_results_by_site(
            ...         359366,
            ...         tmin=datetime(2020, 1, 1, tzinfo=timezone.utc),
            ...         tmax=datetime(2021, 1, 1, tzinfo=timezone.utc)
            ...     )
        """
        key = self._site_lookup.key(
            {
                "national_site_id": national_site_id,
                "site_id": site_id,
                "site_name": site_name,
            }
        )

        return self._results.query(
            where={RESULT_SITE_FIELD: key},
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
            SGUNotFoundError: If any site_id or site_name matches no site.
            ValueError: If not exactly one site identifier is provided, or if a
                looked-up site has no national_site_id.

        Example:

            >>> from sgu_client import SGUClient
            >>> with SGUClient() as client:
            ...     # get results for multiple sites
            ...     results = client.chemistry.get_results_by_sites(
            ...         [359366, 378865],
            ...         tmin="2020-01-01T00:00:00Z",
            ...         tmax="2021-01-01T00:00:00Z",
            ...         limit=1000
            ...     )
            ...     print(f"Found {len(results.features)} analysis results")
        """
        keys = self._site_lookup.keys(
            {
                "national_site_id": national_site_id,
                "site_id": site_id,
                "site_name": site_name,
            }
        )

        return self._results.query(
            where={RESULT_SITE_FIELD: keys},
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
            SGUNotFoundError: If any site_id or site_name matches no site.
            ValueError: If more than one site identifier is provided, or if a
                looked-up site has no national_site_id.

        Example:

            >>> from sgu_client import SGUClient
            >>> with SGUClient() as client:
            ...     # get all lead measurements since 2020
            ...     results = client.chemistry.get_results_by_parameter(
            ...         parameter="Bly",
            ...         tmin="2020-01-01",
            ...     )
            ...     # get pH measurements for a specific site
            ...     results = client.chemistry.get_results_by_parameter(
            ...         parameter="pH",
            ...         national_site_id=359366,
            ...         tmin="2020-01-01",
            ...         tmax="2021-01-01"
            ...     )
            ...     # ... or multiple sites
            ...     results = client.chemistry.get_results_by_parameter(
            ...         parameter="pH",
            ...         national_site_id=[359366, 378865]
            ...     )
        """
        where: Where = {"parameternamn": parameter}

        keys = self._site_lookup.keys(
            {
                "national_site_id": national_site_id,
                "site_id": site_id,
                "site_name": site_name,
            },
            required=False,
        )
        if keys is not None:
            where[RESULT_SITE_FIELD] = keys

        return self._results.query(
            where=where, tmin=tmin, tmax=tmax, limit=limit, **kwargs
        )
