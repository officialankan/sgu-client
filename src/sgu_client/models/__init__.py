"""Models module for SGU Client."""

from .base import SGUBaseModel, SGUResponse
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
    "SGUBaseModel",
    "SGUResponse",
]
