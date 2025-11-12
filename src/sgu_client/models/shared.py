"""Shared types (like GeoJSON objects)"""

from typing import Any, Literal

from pydantic import Field

from sgu_client.models.base import SGUBaseModel


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


class Point(SGUBaseModel):
    """GeoJSON Point geometry."""

    type: Literal["Point"] = "Point"
    coordinates: list[float] = Field(..., min_length=2, max_length=3)


class MultiPoint(SGUBaseModel):
    """GeoJSON MultiPoint geometry."""

    type: Literal["MultiPoint"] = "MultiPoint"
    coordinates: list[list[float]]


class LineString(SGUBaseModel):
    """GeoJSON LineString geometry."""

    type: Literal["LineString"] = "LineString"
    coordinates: list[list[float]] = Field(..., min_length=2)


class Polygon(SGUBaseModel):
    """GeoJSON Polygon geometry."""

    type: Literal["Polygon"] = "Polygon"
    coordinates: list[list[list[float]]]


class MultiPolygon(SGUBaseModel):
    """GeoJSON MultiPolygon geometry."""

    type: Literal["MultiPolygon"] = "MultiPolygon"
    coordinates: list[list[list[list[float]]]]


# Union type for all geometry types
Geometry = Point | MultiPoint | LineString | Polygon | MultiPolygon
