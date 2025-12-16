"""Pydantic models for groundwater chemistry data from SGU API."""

from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from sgu_client.models.base import SGUBaseModel, SGUResponse
from sgu_client.models.shared import CRS, Geometry, Link
from sgu_client.utils.pandas_helpers import get_pandas, optional_pandas_method

if TYPE_CHECKING:
    import pandas as pd


# Sampling site properties (English field names with Swedish API aliases)
class SamplingSiteProperties(SGUBaseModel):
    """Properties for a groundwater chemistry sampling site."""

    # Site identification
    station_id: str | None = Field(
        None, alias="platsbeteckning", description="Station identifier"
    )
    site_name: str | None = Field(
        None, alias="provplatsnamn", description="Sampling site name"
    )
    national_site_id: int | None = Field(
        None, alias="nationellt_provplatsid", description="National sampling site ID"
    )
    eu_station_code: str | None = Field(
        None, alias="eucd_stn", description="EU station code"
    )
    eu_groundwater_body: str | None = Field(
        None, alias="eucd_gwb", description="EU groundwater body"
    )

    # Site classification
    site_type_code: str | None = Field(
        None, alias="provplatstyp", description="Sampling site type code"
    )
    site_type_description: str | None = Field(
        None, alias="provplatstyp_tx", description="Sampling site type description"
    )
    site_category_code: str | None = Field(
        None,
        alias="provplatskat_bedgr",
        description="Sampling site category code (assessment basis)",
    )
    site_category_description: str | None = Field(
        None,
        alias="provplatskat_bedgr_tx",
        description="Sampling site category description",
    )

    # Coordinates (projected)
    north_coordinate: float | None = Field(
        None, alias="n", description="North coordinate"
    )
    east_coordinate: float | None = Field(
        None, alias="e", description="East coordinate"
    )

    # Position metadata
    positioning_method_code: str | None = Field(
        None, alias="positioneringsmetod", description="Positioning method code"
    )
    positioning_method_description: str | None = Field(
        None,
        alias="positioneringsmetod_tx",
        description="Positioning method description",
    )
    position_quality_code: str | None = Field(
        None, alias="positionskvalitet", description="Position quality code"
    )
    position_quality_description: str | None = Field(
        None, alias="positionskvalitet_tx", description="Position quality description"
    )

    # Administrative location
    county_code: str | None = Field(None, alias="lanskod", description="County code")
    county: str | None = Field(None, alias="lan", description="County")
    municipality_code: str | None = Field(
        None, alias="kommunkod", description="Municipality code"
    )
    municipality: str | None = Field(None, alias="kommun", description="Municipality")
    region_code: str | None = Field(
        None, alias="region_bdgr", description="Region code (assessment basis)"
    )
    region_description: str | None = Field(
        None, alias="region_bdgr_tx", description="Region description"
    )
    water_district_code: str | None = Field(
        None, alias="vattendistrikt", description="Water district code"
    )
    water_district_description: str | None = Field(
        None, alias="vattendistrikt_tx", description="Water district description"
    )

    # Well/site characteristics
    reference_level: float | None = Field(
        None, alias="refniva", description="Reference level"
    )
    elevation_system: str | None = Field(
        None, alias="hojdsystem", description="Elevation reference system"
    )
    well_depth: float | None = Field(None, alias="brunnsdjup", description="Well depth")
    well_depth_qualifier: str | None = Field(
        None, alias="tecken_brunnsdjup", description="Well depth sign/qualifier"
    )
    filter_depth_top: float | None = Field(
        None, alias="filterdjup_fran", description="Filter depth from (top)"
    )
    filter_depth_bottom: float | None = Field(
        None, alias="filterdjup_till", description="Filter depth to (bottom)"
    )
    filter_depth_qualifier: str | None = Field(
        None, alias="tecken_filterdjup", description="Filter depth sign/qualifier"
    )

    # Aquifer information
    aquifer_code: str | None = Field(None, alias="akvifer", description="Aquifer code")
    aquifer_description: str | None = Field(
        None, alias="akvifer_tx", description="Aquifer description"
    )

    # Geology
    soil_genesis_code: str | None = Field(
        None, alias="genes_jord", description="Soil genesis code"
    )
    soil_genesis_description: str | None = Field(
        None, alias="genes_jord_tx", description="Soil genesis description"
    )
    rock_type_code: str | None = Field(
        None, alias="bergart", description="Rock type code"
    )
    rock_type_description: str | None = Field(
        None, alias="bergart_tx", description="Rock type description"
    )

    # Site history and monitoring
    established_date: str | None = Field(
        None, alias="etabldatum", description="Site establishment date"
    )  # ISO date string
    decommissioned_date: str | None = Field(
        None, alias="nedlagdatum", description="Site decommissioning date"
    )  # ISO date string
    sample_count: int | None = Field(
        None, alias="antal_prov", description="Number of samples collected"
    )
    program_affiliation: str | None = Field(
        None, alias="programkoppl", description="Program affiliation/connections"
    )

    # Monitoring program flags
    national_monitoring: str | None = Field(
        None, alias="nationell", description="National monitoring program (ja/nej)"
    )
    regional_monitoring: str | None = Field(
        None, alias="regional", description="Regional monitoring program (ja/nej)"
    )
    local_monitoring: str | None = Field(
        None, alias="lokal", description="Local monitoring program (ja/nej)"
    )

    # Classification and symbols
    symbol: str | None = Field(
        None, alias="symbol", description="Symbol/classification marker"
    )

    # Analysis result links
    analyses_csv_url: str | None = Field(
        None, alias="analyser_csv", description="URL to CSV file with analysis results"
    )
    analyses_json_url: str | None = Field(
        None,
        alias="analyser_json",
        description="URL to JSON file with analysis results",
    )

    @property
    def established_datetime(self) -> datetime | None:
        """Parse establishment date as datetime object."""
        if self.established_date:
            try:
                return datetime.fromisoformat(
                    self.established_date.replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                return None
        return None

    @property
    def decommissioned_datetime(self) -> datetime | None:
        """Parse decommissioning date as datetime object."""
        if self.decommissioned_date:
            try:
                return datetime.fromisoformat(
                    self.decommissioned_date.replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                return None
        return None


class SamplingSite(SGUBaseModel):
    """A groundwater chemistry sampling site (GeoJSON Feature)."""

    type: Literal["Feature"] = "Feature"
    id: str = Field(..., description="Site ID")
    geometry: Geometry | None = Field(None, description="Site geometry")
    properties: SamplingSiteProperties = Field(..., description="Site properties")


# Analysis result properties (English field names with Swedish API aliases)
class AnalysisResultProperties(SGUBaseModel):
    """Properties for a groundwater chemistry analysis result."""

    # Site identification
    station_id: str | None = Field(
        None, alias="platsbeteckning", description="Station identifier"
    )
    national_site_id: int | None = Field(
        None, alias="nationellt_provplatsid", description="National sampling site ID"
    )
    county_code: str | None = Field(None, alias="lan", description="County code")

    # Sample identification
    sample_id: str | None = Field(None, alias="provid", description="Sample ID")
    sample_type: str | None = Field(None, alias="provtyp", description="Sample type")
    delivery_id: str | None = Field(None, alias="inlevid", description="Delivery ID")

    # Monitoring program
    program_name: str | None = Field(
        None, alias="programnamn", description="Monitoring program name"
    )
    program_id: str | None = Field(
        None, alias="programid", description="Monitoring program ID"
    )
    monitoring_manual: str | None = Field(
        None, alias="overvakningsmanual", description="Monitoring manual reference"
    )

    # Dates
    sampling_date: str | None = Field(
        None, alias="provtagningsdat", description="Sampling date"
    )  # ISO datetime string
    submission_date: str | None = Field(
        None, alias="inlamningsdat", description="Sample submission date"
    )  # ISO datetime string

    # Parameter (chemical substance measured)
    parameter_name: str | None = Field(
        None, alias="param", description="Parameter/chemical substance name"
    )
    parameter_short_name: str | None = Field(
        None, alias="param_kort", description="Short parameter name"
    )
    parameter_sequence_number: int | None = Field(
        None, alias="paramlopnr", description="Parameter sequence number"
    )

    # Sample and analysis preparation
    water_preparation: str | None = Field(
        None, alias="vattenberedn", description="Water sample preparation"
    )
    sample_preparation: str | None = Field(
        None, alias="provberedn", description="Sample preparation method"
    )

    # Laboratory and method
    laboratory: str | None = Field(None, alias="labb", description="Laboratory name")
    method: str | None = Field(None, alias="metod", description="Analysis method used")

    # Detection and reporting limits
    reporting_limit: float | None = Field(
        None, alias="rapporteringsgrans", description="Reporting limit"
    )
    detection_limit: float | None = Field(
        None, alias="detektionsgrans", description="Detection limit"
    )

    # Measurement value
    measurement_value_annotation: str | None = Field(
        None,
        alias="matvardetalanm",
        description="Measurement value annotation/qualifier",
    )
    measurement_value: float | None = Field(
        None, alias="matvardetal", description="Measurement value (numeric)"
    )
    measurement_value_span: str | None = Field(
        None, alias="matvardespar", description="Measurement value span/range"
    )
    measurement_value_text: str | None = Field(
        None, alias="matvardetext", description="Measurement value as text"
    )
    unit: str | None = Field(None, alias="enhet", description="Unit of measurement")
    measurement_uncertainty: str | None = Field(
        None, alias="matosakerhet", description="Measurement uncertainty"
    )

    # Metadata
    last_updated: str | None = Field(
        None, alias="lastupdate", description="Last update timestamp"
    )  # ISO datetime string
    row_number: int | None = Field(None, alias="radnummer", description="Row number")

    @property
    def sampling_datetime(self) -> datetime | None:
        """Parse sampling date as datetime object."""
        if self.sampling_date:
            try:
                return datetime.fromisoformat(self.sampling_date.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        return None

    @property
    def submission_datetime(self) -> datetime | None:
        """Parse submission date as datetime object."""
        if self.submission_date:
            try:
                return datetime.fromisoformat(
                    self.submission_date.replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                return None
        return None

    @property
    def last_updated_datetime(self) -> datetime | None:
        """Parse last update as datetime object."""
        if self.last_updated:
            try:
                return datetime.fromisoformat(self.last_updated.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        return None


class AnalysisResult(SGUBaseModel):
    """A groundwater chemistry analysis result (GeoJSON Feature)."""

    type: Literal["Feature"] = "Feature"
    id: str = Field(..., description="Result ID")
    geometry: Geometry | None = Field(None, description="Result geometry")
    properties: AnalysisResultProperties = Field(
        ..., description="Analysis result properties"
    )


# Collection response models
class SamplingSiteCollection(SGUResponse):
    """Collection of groundwater chemistry sampling sites (GeoJSON FeatureCollection)."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[SamplingSite] = Field(
        default_factory=list, description="Sampling site features"
    )

    # OGC API Features metadata
    totalFeatures: int | None = Field(None, description="Total number of features")
    numberMatched: int | None = Field(
        None, description="Number of features matching query"
    )
    numberReturned: int | None = Field(None, description="Number of features returned")
    timeStamp: str | None = Field(None, description="Response timestamp")

    # Links and CRS
    links: list[Link] | None = Field(None, description="Related links")
    crs: CRS | None = Field(None, description="Coordinate reference system")

    @optional_pandas_method("to_dataframe() method")
    def to_dataframe(self) -> "pd.DataFrame":
        """Convert to pandas DataFrame with flattened sampling site properties.

        Returns:
            DataFrame containing sampling site data with parsed datetime columns.

        Examples:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> sites = client.chemistry.get_sampling_sites(limit=10)
            >>> df = sites.to_dataframe()
            >>>
            >>> # dataFrame includes site properties with datetime parsing
            >>> print(df[['station_id', 'site_name', 'municipality', 'established_date', 'sample_count']].head())
            >>> # established_date and decommissioned_date are parsed as datetime objects
        """
        data = []
        for feature in self.features:
            row = {
                "site_id": feature.id,
            }
            # Add geometry if present
            if feature.geometry:
                row.update(
                    {
                        "geometry_type": feature.geometry.type,
                        "longitude": feature.geometry.coordinates[0]
                        if feature.geometry.coordinates
                        else None,
                        "latitude": feature.geometry.coordinates[1]
                        if len(feature.geometry.coordinates) > 1
                        else None,
                    }
                )

            # Add parsed datetime columns
            row["established_date"] = feature.properties.established_datetime
            row["decommissioned_date"] = feature.properties.decommissioned_datetime

            # Add all properties
            row.update(feature.properties.model_dump())
            data.append(row)

        pd = get_pandas()
        df = pd.DataFrame(data)

        # Ensure datetime columns are properly typed
        if not df.empty:
            if "established_date" in df.columns:
                df["established_date"] = pd.to_datetime(df["established_date"])
            if "decommissioned_date" in df.columns:
                df["decommissioned_date"] = pd.to_datetime(df["decommissioned_date"])

        return df


class AnalysisResultCollection(SGUResponse):
    """Collection of groundwater chemistry analysis results (GeoJSON FeatureCollection)."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[AnalysisResult] = Field(
        default_factory=list, description="Analysis result features"
    )

    # OGC API Features metadata
    totalFeatures: int | None = Field(None, description="Total number of features")
    numberMatched: int | None = Field(
        None, description="Number of features matching query"
    )
    numberReturned: int | None = Field(None, description="Number of features returned")
    timeStamp: str | None = Field(None, description="Response timestamp")

    # Links and CRS
    links: list[Link] | None = Field(None, description="Related links")
    crs: CRS | None = Field(None, description="Coordinate reference system")

    @optional_pandas_method("to_dataframe() method")
    def to_dataframe(self, sort_by_date: bool = True) -> "pd.DataFrame":
        """Convert to pandas DataFrame with analysis result data.

        Args:
            sort_by_date: Whether to sort the DataFrame by sampling date.

        Returns:
            DataFrame containing analysis result data.

        Examples:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>>
            >>> results = client.chemistry.get_results_by_site(site_id="10001_1", limit=100)
            >>> df = results.to_dataframe()
            >>>
            >>> # dataFrame includes chemical analysis results with multiple datetime columns
            >>> print(df[['sampling_date', 'parameter_short_name', 'measurement_value', 'unit']].head())
            >>> # sampling_date, submission_date, and last_update are all parsed as datetime objects
        """
        data = []
        for feature in self.features:
            row = {
                "result_id": feature.id,
                "sampling_date": feature.properties.sampling_datetime,
                "submission_date": feature.properties.submission_datetime,
                "last_update": feature.properties.last_updated_datetime,
            }

            # Add geometry if present
            if feature.geometry:
                row.update(
                    {
                        "geometry_type": feature.geometry.type,
                        "longitude": feature.geometry.coordinates[0]
                        if feature.geometry.coordinates
                        else None,
                        "latitude": feature.geometry.coordinates[1]
                        if len(feature.geometry.coordinates) > 1
                        else None,
                    }
                )

            # Add all properties
            row.update(feature.properties.model_dump())
            data.append(row)

        pd = get_pandas()
        df = pd.DataFrame(data)

        # Ensure datetime columns are properly typed
        if not df.empty:
            if "sampling_date" in df.columns:
                df["sampling_date"] = pd.to_datetime(df["sampling_date"])
            if "submission_date" in df.columns:
                df["submission_date"] = pd.to_datetime(df["submission_date"])
            if "last_update" in df.columns:
                df["last_update"] = pd.to_datetime(df["last_update"])

        if sort_by_date and not df.empty and "sampling_date" in df.columns:
            df = df.sort_values(by="sampling_date")

        return df

    @optional_pandas_method("to_series() method")
    def to_series(
        self,
        index: str | None = None,
        data: str | None = None,
        sort_by_date: bool = True,
    ) -> "pd.Series":
        """Convert to pandas Series with analysis result data.

        Args:
            index: Column name to use as index. If None, `sampling_date` is used.
            data: Column name to use as data. If None, `measurement_value` is used.
            sort_by_date: Whether to sort the data by sampling date before creating the Series.

        Returns:
            Series containing analysis result data.

        Examples:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>> results = client.chemistry.get_results_by_site(site_id="10001_1", limit=100)
            >>>
            >>> # create time series with default columns (sampling_date, measurement_value)
            >>> series = results.to_series()
            >>> print(series.head())
            >>>
            >>> # use custom columns - e.g., parameter names as data
            >>> series_params = results.to_series(
            ...     index="sampling_date",
            ...     data="parameter_short_name"
            ... )
        """
        df = self.to_dataframe(sort_by_date=sort_by_date)
        pd = get_pandas()

        if data is None:
            data = "measurement_value"
        if index is None:
            index = "sampling_date"

        if df.empty:
            return pd.Series(dtype=float)

        if index and index not in df.columns:
            raise ValueError(f"Index column '{index}' not found in DataFrame.")

        if data and data not in df.columns:
            raise ValueError(f"Data column '{data}' not found in DataFrame.")

        series = pd.Series(data=df[data].values, index=df[index] if index else None)
        series.name = data
        return series

    @optional_pandas_method("pivot_by_parameter() method")
    def pivot_by_parameter(
        self,
        values: str = "measurement_value",
        index: str = "sampling_date",
        columns: str = "parameter_short_name",
        aggfunc: str = "mean",
    ) -> "pd.DataFrame":
        """Pivot analysis results by parameter for easier time series analysis.

        This creates a wide-format DataFrame where each chemical parameter becomes
        a column, making it easy to analyze multiple parameters over time.

        Args:
            values: Column to use for values (default: 'measurement_value')
            index: Column to use as index (default: 'sampling_date')
            columns: Column to pivot into columns (default: 'parameter_short_name')
            aggfunc: Aggregation function if there are duplicate index/column pairs
                    (default: 'mean'). Can be 'mean', 'median', 'first', 'last', etc.

        Returns:
            Pivoted DataFrame with parameters as columns.

        Example:

            >>> from sgu_client import SGUClient()
            >>> client = SGUClient()
            >>>
            >>> results = client.chemistry.get_results_by_site(site_id="10001_1")
            >>> df_pivot = results.pivot_by_parameter()
            >>> # now df_pivot has columns like 'PH', 'NITRATE', 'CHLORIDE', etc.
        """
        df = self.to_dataframe(sort_by_date=True)
        pd = get_pandas()

        if df.empty:
            return pd.DataFrame()

        # Validate columns exist
        for col in [values, index, columns]:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in DataFrame.")

        # Create pivot table
        pivot_df = df.pivot_table(
            values=values, index=index, columns=columns, aggfunc=aggfunc
        )

        return pivot_df
