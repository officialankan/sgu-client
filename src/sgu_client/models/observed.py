"""Pydantic models for groundwater data from SGU API."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field

from sgu_client.models.base import SGUBaseModel, SGUResponse
from sgu_client.models.shared import Geometry
from sgu_client.utils.pandas_helpers import get_pandas, optional_pandas_method

if TYPE_CHECKING:
    import pandas as pd


# Groundwater station properties (Swedish API field names)
class GroundwaterStationProperties(SGUBaseModel):
    """Properties for a groundwater monitoring station."""

    # Station identification
    rowid: int = Field(..., description="Row ID")
    platsbeteckning: str | None = Field(None, description="Platsbeteckning")
    obsplatsnamn: str | None = Field(None, description="Observation place name")
    provplatsid: str | None = Field(None, description="Sample site ID")

    # Time period
    fdat: str | None = Field(None, description="From date")  # ISO date string
    tdat: str | None = Field(None, description="To date")  # ISO date string

    # Elevation and reference
    refniva: float | None = Field(None, description="Reference level")
    hojdmetod: str | None = Field(None, description="Height method")
    hojdsystem: str | None = Field(None, description="Height system")
    rorhojd: float | None = Field(None, description="Pipe height")
    rorlangd: float | None = Field(None, description="Pipe length")

    # Aquifer information
    akvifer: str | None = Field(None, description="Aquifer code")
    akvifer_tx: str | None = Field(None, description="Aquifer description")

    # Geology
    jordart: str | None = Field(None, description="Soil type code")
    jordart_tx: str | None = Field(None, description="Soil type description")
    genes_jord: str | None = Field(None, description="Soil genesis code")
    genes_jord_tx: str | None = Field(None, description="Soil genesis description")
    jord_ovan_jord: str | None = Field(None, description="Soil above soil")
    jord_ovan_jord_tx: str | None = Field(
        None, description="Soil above soil description"
    )
    jorddjup: float | None = Field(None, description="Soil depth")
    tecken_jorddjup: str | None = Field(None, description="Soil depth sign")

    # Well construction
    idiam: float | None = Field(None, description="Inner diameter")
    brunnsmtrl: str | None = Field(None, description="Well material")
    brunnsmtrl_tx: str | None = Field(None, description="Well material description")
    borrhalslutning: str | None = Field(None, description="Borehole closure")
    sillangd: float | None = Field(None, description="Screen length")

    # Hydrogeological setting
    geohylag: str | None = Field(None, description="Geohydrological position code")
    geohylag_tx: str | None = Field(
        None, description="Geohydrological position description"
    )

    # Administrative
    kommunkod: str | None = Field(None, description="Municipality code")
    kommun: str | None = Field(None, description="Municipality")
    lanskod: str | None = Field(None, description="County code")
    lan: str | None = Field(None, description="County")
    eucd_gwb: str | None = Field(None, description="EU groundwater body")

    # Coordinates (projected)
    n: float | None = Field(None, description="North coordinate")
    e: float | None = Field(None, description="East coordinate")

    # Symbols and notes
    symbol_magasin: str | None = Field(None, description="Aquifer symbol")
    symbol_paverkan: str | None = Field(None, description="Impact symbol")
    stationsanmarkning: str | None = Field(None, description="Station note")
    kommentar: str | None = Field(None, description="Comment")


class GroundwaterStation(SGUBaseModel):
    """A groundwater monitoring station (GeoJSON Feature)."""

    type: Literal["Feature"] = "Feature"
    id: str = Field(..., description="Station ID")
    geometry: Geometry = Field(..., description="Station geometry")
    properties: GroundwaterStationProperties = Field(
        ..., description="Station properties"
    )


# Groundwater measurement properties
class GroundwaterMeasurementProperties(SGUBaseModel):
    """Properties for a groundwater level measurement."""

    # Identification
    rowid: int = Field(..., description="Row ID")
    platsbeteckning: str | None = Field(None, description="Platsbeteckning")

    # Measurement data
    obsdatum: str | None = Field(
        None, description="Observation date"
    )  # ISO datetime string
    grundvattenniva_m_urok: float | None = Field(
        None, description="Groundwater level (m below ground)"
    )
    grundvattenniva_m_o_h: float | None = Field(
        None, description="Groundwater level (m above sea level)"
    )
    grundvattenniva_m_u_markyta: float | None = Field(
        None, description="Groundwater level (m below surface)"
    )

    # Measurement method and quality
    metod_for_matning: str | None = Field(None, description="Measurement method")
    nivaanmarkning: str | None = Field(None, description="Level note")

    # Metadata
    lastupdate: str | None = Field(
        None, description="Last update"
    )  # ISO datetime string

    @property
    def observation_date(self) -> datetime | None:
        """Parse observation date as datetime object."""
        if self.obsdatum:
            try:
                return datetime.fromisoformat(self.obsdatum.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        return None

    @property
    def last_update_date(self) -> datetime | None:
        """Parse last update as datetime object."""
        if self.lastupdate:
            try:
                return datetime.fromisoformat(self.lastupdate.replace("Z", "+00:00"))
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
class Link(SGUBaseModel):
    """A link in a GeoJSON response."""

    href: str = Field(..., description="Link URL")
    rel: str | None = Field(None, description="Link relation")
    type: str | None = Field(None, description="Link media type")
    title: str | None = Field(None, description="Link title")


class CRS(SGUBaseModel):
    """Coordinate Reference System."""

    type: str = Field(..., description="CRS type")
    properties: dict[str, Any] = Field(..., description="CRS properties")


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
        """Convert to pandas DataFrame with flattened station properties."""

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
        """

        data = []
        for feature in self.features:
            row = {
                "measurement_id": feature.id,
                "observation_date": feature.properties.observation_date,
                "last_update": feature.properties.last_update_date,
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
            data: Column name to use as data. If None, `grundvattenniva_m_o_h` is used.
            sort_by_date: Whether to sort the data by observation date before creating the Series.

        Returns:
            Series containing measurement data.
        """
        df = self.to_dataframe(sort_by_date=sort_by_date)
        pd = get_pandas()

        if data is None:
            data = "grundvattenniva_m_o_h"
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
