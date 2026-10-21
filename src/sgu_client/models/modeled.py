"""Pydantic models for modeled groundwater data from SGU API."""

from typing import ClassVar

from pydantic import Field, field_validator

from sgu_client.models.base import SGUBaseModel
from sgu_client.models.dates import ApiDatetime
from sgu_client.models.features import Feature, FeatureCollection, TimeSeriesCollection


# Modeled area properties (from omraden collection)
class ModeledAreaProperties(SGUBaseModel):
    """Properties for a modeled groundwater area."""

    model_config: ClassVar = {"validate_by_name": True, "validate_by_alias": True}

    area_id: int = Field(..., alias="omrade_id", description="Area ID")
    time_series_url: str | None = Field(
        None, alias="url_tidsserie", description="Time series URL for this area"
    )


class ModeledArea(Feature[ModeledAreaProperties]):
    """A modeled groundwater area (GeoJSON Feature)."""


# Modeled groundwater level properties (from grundvattennivaer-tidigare collection)
class ModeledGroundwaterLevelProperties(SGUBaseModel):
    """Properties for a modeled groundwater level."""

    model_config: ClassVar = {"validate_by_name": True, "validate_by_alias": True}

    # Date and area identification
    date: ApiDatetime = Field(None, alias="datum", description="Date (midnight UTC)")
    area_id: int = Field(..., alias="omrade_id", description="Area ID")

    # Deviation percentiles (0-100)
    deviation_small_resources: int | None = Field(
        None,
        alias="grundvattensituation_sma",
        description="Deviation for small resources (percentile 0-100)",
    )
    deviation_large_resources: int | None = Field(
        None,
        alias="grundvattensituation_stora",
        description="Deviation for large resources (percentile 0-100)",
    )

    # Relative level percentiles (0-100)
    relative_level_small_resources: int | None = Field(
        None,
        alias="fyllnadsgrad_sma",
        description="Relative level for small resources (percentile 0-100)",
    )
    relative_level_large_resources: int | None = Field(
        None,
        alias="fyllnadsgrad_stora",
        description="Relative level for large resources (percentile 0-100)",
    )

    # Object identifier
    object_id: int = Field(..., alias="objectid", description="Object ID")

    @field_validator(
        "deviation_large_resources", "relative_level_large_resources", mode="before"
    )
    @classmethod
    def transform_missing_values(cls, v):
        """Transform -1 values to None for large resource fields."""
        return None if v == -1 else v


class ModeledGroundwaterLevel(Feature[ModeledGroundwaterLevelProperties]):
    """A modeled groundwater level (GeoJSON Feature)."""


# Collection response models
class ModeledAreaCollection(FeatureCollection[ModeledArea]):
    """Collection of modeled groundwater areas (GeoJSON FeatureCollection).

    Areas are grid cells, so the DataFrame has ``centroid_longitude`` and
    ``centroid_latitude`` columns: the centre of the cell. SGU sends only the
    cell's outline; the centre is computed by sgu-client.

    Examples:

        >>> from sgu_client import SGUClient
        >>> with SGUClient() as client:
        ...     areas = client.levels.modeled.get_areas(limit=10)
        ...     df = areas.to_dataframe()
        ...     print(df[['area_id', 'centroid_longitude', 'centroid_latitude']].head())
    """

    _geometry = "centroid"


class ModeledGroundwaterLevelCollection(TimeSeriesCollection[ModeledGroundwaterLevel]):
    """Collection of modeled groundwater levels (GeoJSON FeatureCollection).

    Its DataFrame has no geometry columns. Sorted by ``date``; ``to_series()``
    defaults to ``relative_level_small_resources``.

    Examples:

        >>> from sgu_client import SGUClient
        >>> with SGUClient() as client:
        ...     levels = client.levels.modeled.get_levels(limit=100)
        ...     df = levels.to_dataframe()
        ...     print(df[['date', 'area_id', 'relative_level_small_resources']].head())
        ...     series = levels.to_series(data="relative_level_large_resources")
    """

    _date_column = "date"
    _series_column = "relative_level_small_resources"
