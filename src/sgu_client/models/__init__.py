"""Models module for SGU Client."""

from .base import SGUBaseModel, SGUResponse
from .modeled import (
    ModeledArea,
    ModeledAreaCollection,
    ModeledAreaProperties,
    ModeledGroundwaterLevel,
    ModeledGroundwaterLevelCollection,
    ModeledGroundwaterLevelProperties,
)
from .observed import (
    GroundwaterMeasurement,
    GroundwaterMeasurementCollection,
    GroundwaterMeasurementProperties,
    GroundwaterStation,
    GroundwaterStationCollection,
    GroundwaterStationProperties,
)

__all__ = [
    "GroundwaterMeasurement",
    "GroundwaterMeasurementCollection",
    "GroundwaterMeasurementProperties",
    "GroundwaterStation",
    "GroundwaterStationCollection",
    "GroundwaterStationProperties",
    "ModeledArea",
    "ModeledAreaCollection",
    "ModeledAreaProperties",
    "ModeledGroundwaterLevel",
    "ModeledGroundwaterLevelCollection",
    "ModeledGroundwaterLevelProperties",
    "SGUBaseModel",
    "SGUResponse",
]
