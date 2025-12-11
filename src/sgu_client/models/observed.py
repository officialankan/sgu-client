"""Pydantic models for groundwater data from SGU API."""

from datetime import datetime
from typing import TYPE_CHECKING, Literal

from pydantic import Field

from sgu_client.models.base import SGUBaseModel, SGUResponse
from sgu_client.models.shared import CRS, Geometry, Link
from sgu_client.utils.pandas_helpers import get_pandas, optional_pandas_method

if TYPE_CHECKING:
    import pandas as pd


# Groundwater station properties (English field names with Swedish API aliases)
class GroundwaterStationProperties(SGUBaseModel):
    """Properties for a groundwater monitoring station."""

    # Station identification
    row_id: int = Field(..., alias="rowid", description="Row ID")
    station_id: str | None = Field(
        None, alias="platsbeteckning", description="Station identifier"
    )
    station_name: str | None = Field(
        None, alias="obsplatsnamn", description="Observation station name"
    )
    sample_site_id: str | None = Field(
        None, alias="provplatsid", description="Sample site ID"
    )

    # Time period
    active_since: str | None = Field(
        None, alias="fdat", description="Active since date"
    )  # ISO date string
    active_until: str | None = Field(
        None, alias="tdat", description="Active until date"
    )  # ISO date string

    # Elevation and reference
    reference_level: float | None = Field(
        None, alias="refniva", description="Reference level"
    )
    elevation_method: str | None = Field(
        None, alias="hojdmetod", description="Height/elevation measurement method"
    )
    elevation_system: str | None = Field(
        None, alias="hojdsystem", description="Height/elevation reference system"
    )
    well_height: float | None = Field(None, alias="rorhojd", description="Pipe height")
    well_length: float | None = Field(None, alias="rorlangd", description="Pipe length")

    # Aquifer information
    aquifer_code: str | None = Field(None, alias="akvifer", description="Aquifer code")
    aquifer_description: str | None = Field(
        None, alias="akvifer_tx", description="Aquifer description"
    )

    # Geology
    soil_code: str | None = Field(None, alias="jordart", description="Soil type code")
    soil_description: str | None = Field(
        None, alias="jordart_tx", description="Soil type description"
    )
    soil_genesis_code: str | None = Field(
        None, alias="genes_jord", description="Soil genesis code"
    )
    soil_genesis_description: str | None = Field(
        None, alias="genes_jord_tx", description="Soil genesis description"
    )
    overlying_soil_code: str | None = Field(
        None, alias="jord_ovan_jord", description="Soil above soil code"
    )
    overlying_soil_description: str | None = Field(
        None, alias="jord_ovan_jord_tx", description="Soil above soil description"
    )
    soil_depth: float | None = Field(None, alias="jorddjup", description="Soil depth")
    soil_depth_qualifier: str | None = Field(
        None, alias="tecken_jorddjup", description="Soil depth sign/qualifier"
    )

    # Well construction
    inner_diameter: float | None = Field(
        None, alias="idiam", description="Inner diameter"
    )
    well_material_code: str | None = Field(
        None, alias="brunnsmtrl", description="Well material code"
    )
    well_material_description: str | None = Field(
        None, alias="brunnsmtrl_tx", description="Well material description"
    )
    borehole_completion: float | None = Field(
        None, alias="borrhalslutning", description="Borehole closure/completion"
    )
    screen_length: float | None = Field(
        None, alias="sillangd", description="Screen length"
    )

    # Hydrogeological setting
    hydrogeological_setting_code: str | None = Field(
        None, alias="geohylag", description="Geohydrological position code"
    )
    hydrogeological_setting_description: str | None = Field(
        None, alias="geohylag_tx", description="Geohydrological position description"
    )

    # Administrative
    municipality_code: str | None = Field(
        None, alias="kommunkod", description="Municipality code"
    )
    municipality: str | None = Field(None, alias="kommun", description="Municipality")
    county_code: str | None = Field(None, alias="lanskod", description="County code")
    county: str | None = Field(None, alias="lan", description="County")
    eu_groundwater_body: str | None = Field(
        None, alias="eucd_gwb", description="EU groundwater body"
    )

    # Coordinates (projected)
    north_coordinate: float | None = Field(
        None, alias="n", description="North coordinate"
    )
    east_coordinate: float | None = Field(
        None, alias="e", description="East coordinate"
    )

    # Symbols and notes
    aquifer_symbol: str | None = Field(
        None, alias="symbol_magasin", description="Aquifer symbol"
    )
    impact_symbol: str | None = Field(
        None, alias="symbol_paverkan", description="Impact symbol"
    )
    station_remark: str | None = Field(
        None, alias="stationsanmarkning", description="Station note/remarks"
    )
    comments: str | None = Field(None, alias="kommentar", description="Comment")


class GroundwaterStation(SGUBaseModel):
    """A groundwater monitoring station (GeoJSON Feature)."""

    type: Literal["Feature"] = "Feature"
    id: str = Field(..., description="Station ID")
    geometry: Geometry = Field(..., description="Station geometry")
    properties: GroundwaterStationProperties = Field(
        ..., description="Station properties"
    )


# Groundwater measurement properties (English field names with Swedish API aliases)
class GroundwaterMeasurementProperties(SGUBaseModel):
    """Properties for a groundwater level measurement."""

    # Identification
    row_id: int = Field(..., alias="rowid", description="Row ID")
    station_id: str | None = Field(
        None, alias="platsbeteckning", description="Station identifier"
    )

    # Measurement data
    observation_date: str | None = Field(
        None, alias="obsdatum", description="Observation date"
    )  # ISO datetime string
    water_level_below_ground_m: float | None = Field(
        None,
        alias="grundvattenniva_m_urok",
        description="Groundwater level (m below ground)",
    )
    water_level_masl_m: float | None = Field(
        None,
        alias="grundvattenniva_m_o_h",
        description="Groundwater level (m above sea level)",
    )
    water_level_below_surface_m: float | None = Field(
        None,
        alias="grundvattenniva_m_u_markyta",
        description="Groundwater level (m below surface)",
    )

    # Measurement method and quality
    measurement_method: str | None = Field(
        None, alias="metod_for_matning", description="Measurement method"
    )
    level_remark: str | None = Field(
        None, alias="nivaanmarkning", description="Level note/remarks"
    )

    # Metadata
    last_updated: str | None = Field(
        None, alias="lastupdate", description="Last update timestamp"
    )  # ISO datetime string

    @property
    def observation_datetime(self) -> datetime | None:
        """Parse observation date as datetime object."""
        if self.observation_date:
            try:
                return datetime.fromisoformat(
                    self.observation_date.replace("Z", "+00:00")
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


class GroundwaterMeasurement(SGUBaseModel):
    """A groundwater level measurement (GeoJSON Feature)."""

    type: Literal["Feature"] = "Feature"
    id: str = Field(..., description="Measurement ID")
    geometry: Geometry | None = Field(None, description="Measurement geometry")
    properties: GroundwaterMeasurementProperties = Field(
        ..., description="Measurement properties"
    )


# Collection response models
class GroundwaterStationCollection(SGUResponse):
    """Collection of groundwater monitoring stations (GeoJSON FeatureCollection)."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GroundwaterStation] = Field(
        default_factory=list, description="Station features"
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
    def to_dataframe(
        self,
    ) -> "pd.DataFrame":
        """Convert to pandas DataFrame with flattened station properties.

        Returns:
            DataFrame containing station data with geometry columns.

        Examples:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>> stations = client.levels.observed.get_stations(limit=10)
            >>> df = stations.to_dataframe()
            >>>
            >>> # dataFrame includes flattened properties and geometry coordinates
            >>> print(df.columns)  # station_id, longitude, latitude, station_name, municipality, etc.
            >>> print(df[['station_id', 'station_name', 'municipality', 'longitude', 'latitude']].head())
        """

        data = []
        for feature in self.features:
            row = {
                "station_id": feature.id,
                "geometry_type": feature.geometry.type,
                "longitude": feature.geometry.coordinates[0]
                if feature.geometry.coordinates
                else None,
                "latitude": feature.geometry.coordinates[1]
                if len(feature.geometry.coordinates) > 1
                else None,
            }
            # Add all properties
            row.update(feature.properties.model_dump())
            data.append(row)

        pd = get_pandas()
        return pd.DataFrame(data)


class GroundwaterMeasurementCollection(SGUResponse):
    """Collection of groundwater level measurements (GeoJSON FeatureCollection)."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GroundwaterMeasurement] = Field(
        default_factory=list, description="Measurement features"
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
        """Convert to pandas DataFrame with measurement data.

        Args
            sort_by_date: Whether to sort the DataFrame by observation date.

        Returns
            DataFrame containing measurement data.

        Examples:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>> measurements = client.levels.observed.get_measurements(limit=100)
            >>> df = measurements.to_dataframe()
            >>>
            >>> # dataFrame is sorted by observation_date by default
            >>> print(df[['observation_date', 'water_level_masl_m', 'station_id']].head())
        """

        data = []
        for feature in self.features:
            row = {
                "measurement_id": feature.id,
                "observation_date": feature.properties.observation_datetime,
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
        if not df.empty and "observation_date" in df.columns:
            df["observation_date"] = pd.to_datetime(df["observation_date"])
        if not df.empty and "last_update" in df.columns:
            df["last_update"] = pd.to_datetime(df["last_update"])

        if sort_by_date:
            df = df.sort_values(by="observation_date")
        return df

    @optional_pandas_method("to_series() method")
    def to_series(
        self,
        index: str | None = None,
        data: str | None = None,
        sort_by_date: bool = True,
    ) -> "pd.Series":
        """Convert to pandas Series with measurement data.

        Args:
            index: Column name to use as index. If None, `observation_date` is used.
            data: Column name to use as data. If None, `water_level_masl_m` is used.
            sort_by_date: Whether to sort the data by observation date before creating the Series.

        Returns:
            Series containing measurement data.

        Examples:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>> measurements = client.levels.observed.get_measurements_by_name(
            ...     platsbeteckning="95_2", limit=100
            ... )
            >>>
            >>> # create time series with default columns (observation_date, water_level_masl_m)
            >>> series = measurements.to_series()
            >>> print(series.head())
            >>>
            >>> # use custom columns for index and data
            >>> series_custom = measurements.to_series(
            ...     index="observation_date",
            ...     data="water_level_below_ground_m"
            ... )
        """
        df = self.to_dataframe(sort_by_date=sort_by_date)
        pd = get_pandas()

        if data is None:
            data = "water_level_masl_m"
        if index is None:
            index = "observation_date"

        if df.empty:
            return pd.Series(dtype=float)

        if index and index not in df.columns:
            raise ValueError(f"Index column '{index}' not found in DataFrame.")

        if data and data not in df.columns:
            raise ValueError(f"Data column '{data}' not found in DataFrame.")

        series = pd.Series(data=df[data].values, index=df[index] if index else None)
        series.name = data
        return series
