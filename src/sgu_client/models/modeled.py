"""Pydantic models for modeled groundwater data from SGU API."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field, field_validator

from sgu_client.models.base import SGUBaseModel, SGUResponse
from sgu_client.models.observed import CRS, Link
from sgu_client.models.shared import Geometry
from sgu_client.utils.pandas_helpers import get_pandas, optional_pandas_method

if TYPE_CHECKING:
    import pandas as pd


# Modeled area properties (from omraden collection)
class ModeledAreaProperties(SGUBaseModel):
    """Properties for a modeled groundwater area."""

    omrade_id: int = Field(..., description="Area ID")
    url_tidsserie: str | None = Field(None, description="Time series URL for this area")


class ModeledArea(SGUBaseModel):
    """A modeled groundwater area (GeoJSON Feature)."""

    type: Literal["Feature"] = "Feature"
    id: str = Field(..., description="Area ID")
    geometry: Geometry = Field(
        ..., description="Area geometry (typically MultiPolygon)"
    )
    properties: ModeledAreaProperties = Field(..., description="Area properties")


# Modeled groundwater level properties (from grundvattennivaer-tidigare collection)
class ModeledGroundwaterLevelProperties(SGUBaseModel):
    """Properties for a modeled groundwater level."""

    # Date and area identification
    datum: str | None = Field(None, description="Date (ISO format)")
    omrade_id: int = Field(..., description="Area ID")

    # Deviation percentiles (0-100)
    grundvattensituation_sma: int | None = Field(
        None, description="Deviation for small resources (percentile 0-100)"
    )
    grundvattensituation_stora: int | None = Field(
        None, description="Deviation for large resources (percentile 0-100)"
    )

    # Relative level percentiles (0-100)
    fyllnadsgrad_sma: int | None = Field(
        None, description="Relative level for small resources (percentile 0-100)"
    )
    fyllnadsgrad_stora: int | None = Field(
        None, description="Relative level for large resources (percentile 0-100)"
    )

    # Object identifier
    objectid: int = Field(..., description="Object ID")

    @field_validator("grundvattensituation_stora", "fyllnadsgrad_stora", mode="before")
    @classmethod
    def transform_missing_values(cls, v):
        """Transform -1 values to None for large resource fields."""
        return None if v == -1 else v

    @property
    def date(self) -> datetime | None:
        """Parse date as datetime object (daily data, no timezone)."""
        if self.datum:
            try:
                # Remove 'Z' suffix and parse as naive datetime (daily data)
                date_str = self.datum.rstrip("Z")
                return datetime.fromisoformat(date_str)
            except (ValueError, AttributeError):
                return None
        return None


class ModeledGroundwaterLevel(SGUBaseModel):
    """A modeled groundwater level (GeoJSON Feature)."""

    type: Literal["Feature"] = "Feature"
    id: str = Field(..., description="Level ID")
    geometry: Geometry | None = Field(
        None, description="Level geometry (typically null)"
    )
    properties: ModeledGroundwaterLevelProperties = Field(
        ..., description="Level properties"
    )


# Collection response models
class ModeledAreaCollection(SGUResponse):
    """Collection of modeled groundwater areas (GeoJSON FeatureCollection)."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[ModeledArea] = Field(
        default_factory=list, description="Area features"
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

    @field_validator("totalFeatures", mode="before")
    @classmethod
    def handle_unknown_total_features(cls, v):
        """Handle 'unknown' string values for totalFeatures."""
        return None if v == "unknown" else v

    @optional_pandas_method("to_dataframe() method")
    def to_dataframe(self) -> "pd.DataFrame":
        """Convert to pandas DataFrame with flattened area properties."""

        data = []
        for feature in self.features:
            row: dict[str, Any] = {
                "area_id": feature.id,
                "geometry_type": feature.geometry.type,
            }

            # Add geometry coordinates (MultiPolygon handling)
            if feature.geometry.coordinates:
                # For MultiPolygon, take centroid of first polygon's first ring
                if feature.geometry.type == "MultiPolygon":
                    try:
                        # MultiPolygon structure: [polygon][ring][point][lon/lat]
                        # Type narrowing: we know this is MultiPolygon, so coordinates is list[list[list[list[float]]]]
                        first_ring = feature.geometry.coordinates[0][0]
                        # Calculate simple centroid
                        lons = [point[0] for point in first_ring]
                        lats = [point[1] for point in first_ring]
                        row["centroid_longitude"] = sum(lons) / len(lons)
                        row["centroid_latitude"] = sum(lats) / len(lats)
                    except (IndexError, TypeError):
                        row["centroid_longitude"] = None
                        row["centroid_latitude"] = None
                else:
                    row["centroid_longitude"] = None
                    row["centroid_latitude"] = None
            else:
                row["centroid_longitude"] = None
                row["centroid_latitude"] = None

            # Add all properties
            row.update(feature.properties.model_dump())
            data.append(row)

        pd = get_pandas()
        return pd.DataFrame(data)


class ModeledGroundwaterLevelCollection(SGUResponse):
    """Collection of modeled groundwater levels (GeoJSON FeatureCollection)."""

    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[ModeledGroundwaterLevel] = Field(
        default_factory=list, description="Level features"
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

    @field_validator("totalFeatures", mode="before")
    @classmethod
    def handle_unknown_total_features(cls, v):
        """Handle 'unknown' string values for totalFeatures."""
        return None if v == "unknown" else v

    @optional_pandas_method("to_dataframe() method")
    def to_dataframe(self, sort_by_date: bool = True) -> "pd.DataFrame":
        """Convert to pandas DataFrame with modeled level data.

        Args:
            sort_by_date: Whether to sort the DataFrame by date.

        Returns:
            DataFrame containing modeled level data.
        """

        data = []
        for feature in self.features:
            row = {
                "level_id": feature.id,
                "date": feature.properties.date,
            }

            # Add all properties
            row.update(feature.properties.model_dump())
            data.append(row)

        pd = get_pandas()
        df = pd.DataFrame(data)
        if sort_by_date and "date" in df.columns:
            df = df.sort_values(by="date")
        return df

    @optional_pandas_method("to_series() method")
    def to_series(
        self,
        index: str | None = None,
        data: str | None = None,
        sort_by_date: bool = True,
    ) -> "pd.Series":
        """Convert to pandas Series with modeled data.

        Args:
            index: Column name to use as index. If None, `date` is used.
            data: Column name to use as data. If None, `fyllnadsgrad_sma` is used.
            sort_by_date: Whether to sort the data by observation date before creating the Series.

        Returns:
            Series containing modeled data.
        """
        df = self.to_dataframe(sort_by_date=sort_by_date)
        pd = get_pandas()

        if data is None:
            data = "fyllnadsgrad_sma"
        if index is None:
            index = "date"

        if df.empty:
            return pd.Series(dtype=float)

        if index and index not in df.columns:
            raise ValueError(f"Index column '{index}' not found in DataFrame.")

        if data and data not in df.columns:
            raise ValueError(f"Data column '{data}' not found in DataFrame.")

        series = pd.Series(data=df[data].values, index=df[index] if index else None)
        series.name = data
        return series
