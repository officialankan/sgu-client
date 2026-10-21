"""Pydantic models for groundwater data from SGU API."""

from pydantic import Field

from sgu_client.models.base import SGUBaseModel
from sgu_client.models.dates import ApiDatetime
from sgu_client.models.features import Feature, FeatureCollection, TimeSeriesCollection


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
    active_since: ApiDatetime = Field(
        None, alias="fdat", description="Active since date (midnight UTC)"
    )
    active_until: ApiDatetime = Field(
        None,
        alias="tdat",
        description="Active until date (midnight UTC); None for a live station",
    )

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


class GroundwaterStation(Feature[GroundwaterStationProperties]):
    """A groundwater monitoring station (GeoJSON Feature).

    ``geometry`` is null for stations without a location.
    """


# Groundwater measurement properties (English field names with Swedish API aliases)
class GroundwaterMeasurementProperties(SGUBaseModel):
    """Properties for a groundwater level measurement."""

    # Identification
    row_id: int = Field(..., alias="rowid", description="Row ID")
    station_id: str | None = Field(
        None, alias="platsbeteckning", description="Station identifier"
    )

    # Measurement data
    observation_date: ApiDatetime = Field(
        None, alias="obsdatum", description="Observation timestamp (UTC)"
    )
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
    last_updated: ApiDatetime = Field(
        None, alias="lastupdate", description="Last update timestamp (UTC)"
    )


class GroundwaterMeasurement(Feature[GroundwaterMeasurementProperties]):
    """A groundwater level measurement (GeoJSON Feature)."""


# Collection response models
class GroundwaterStationCollection(FeatureCollection[GroundwaterStation]):
    """Collection of groundwater monitoring stations (GeoJSON FeatureCollection).

    Its DataFrame has ``longitude`` and ``latitude`` columns, null for stations
    without a location.

    Examples:

        >>> from sgu_client import SGUClient
        >>> with SGUClient() as client:
        ...     stations = client.levels.observed.get_stations(limit=10)
        ...     df = stations.to_dataframe()
        ...     print(df[['station_id', 'station_name', 'longitude', 'latitude']].head())
    """

    _geometry = "point"


class GroundwaterMeasurementCollection(TimeSeriesCollection[GroundwaterMeasurement]):
    """Collection of groundwater level measurements (GeoJSON FeatureCollection).

    Its DataFrame has no geometry columns. Sorted by ``observation_date``;
    ``to_series()`` defaults to ``water_level_masl_m``.

    Examples:

        >>> from sgu_client import SGUClient
        >>> with SGUClient() as client:
        ...     measurements = client.levels.observed.get_measurements_by_name(
        ...         station_id="95_2", limit=100
        ...     )
        ...     df = measurements.to_dataframe()
        ...     print(df[['observation_date', 'water_level_masl_m', 'station_id']].head())
        ...     series = measurements.to_series()
    """

    _date_column = "observation_date"
    _series_column = "water_level_masl_m"
