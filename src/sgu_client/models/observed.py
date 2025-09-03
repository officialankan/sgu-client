"""Pydantic models for groundwater data from SGU API."""

from datetime import datetime
from typing import Any, Literal

import pandas as pd
from pydantic import Field

from sgu_client.models.base import SGUBaseModel, SGUResponse
from sgu_client.models.shared import Geometry


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
    idiam: int | None = Field(None, description="Inner diameter")
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

    def to_dataframe(
        self,
    ) -> pd.DataFrame:
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

    def to_dataframe(self, sort_by_date: bool = True) -> pd.DataFrame:
        """Convert to pandas DataFrame with measurement data.

        Args
            sort_by_date: Whether to sort the DataFrame by observation date.

        Returns
            pd.DataFrame: DataFrame containing measurement data.
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

        df = pd.DataFrame(data)
        if sort_by_date:
            df = df.sort_values(by="observation_date")
        return df
