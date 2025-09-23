"""Tests for Pydantic models in sgu_client.models package."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from sgu_client.models.base import SGUBaseModel, SGUResponse
from sgu_client.models.modeled import (
    ModeledArea,
    ModeledAreaProperties,
    ModeledGroundwaterLevel,
    ModeledGroundwaterLevelProperties,
)
from sgu_client.models.observed import (
    CRS,
    GroundwaterMeasurement,
    GroundwaterMeasurementCollection,
    GroundwaterMeasurementProperties,
    GroundwaterStation,
    GroundwaterStationCollection,
    GroundwaterStationProperties,
    Link,
)
from sgu_client.models.shared import (
    LineString,
    MultiPoint,
    MultiPolygon,
    Point,
    Polygon,
)


def test_sgu_base_model_allows_extra_fields():
    """Test that extra fields are allowed in SGU models."""

    class TestModel(SGUBaseModel):
        name: str

    # Should not raise error with extra field
    model = TestModel(name="test", extra_field="value")
    assert model.name == "test"
    assert hasattr(model, "extra_field")


def test_sgu_base_model_validates_assignment():
    """Test that assignment validation works."""

    class TestModel(SGUBaseModel):
        count: int

    model = TestModel(count=5)
    model.count = 10  # Should work
    assert model.count == 10

    with pytest.raises(ValidationError):
        model.count = "invalid"  # Should fail validation


def test_sgu_response_to_dict():
    """Test conversion to dictionary."""

    class TestResponse(SGUResponse):
        value: str

    response = TestResponse(value="test")
    result = response.to_dict()
    assert result == {"value": "test"}


def test_sgu_response_to_dataframe_not_implemented():
    """Test that base to_dataframe raises NotImplementedError."""

    class TestResponse(SGUResponse):
        value: str

    response = TestResponse(value="test")
    with pytest.raises(NotImplementedError, match="Subclasses must implement"):
        response.to_dataframe()


def test_point_geometry_valid():
    """Test valid Point geometry."""
    point = Point(coordinates=[12.5, 55.7])
    assert point.type == "Point"
    assert point.coordinates == [12.5, 55.7]

    # With elevation
    point_3d = Point(coordinates=[12.5, 55.7, 100.0])
    assert len(point_3d.coordinates) == 3


def test_point_geometry_invalid_coordinates():
    """Test Point with invalid coordinates."""
    with pytest.raises(ValidationError):
        Point(coordinates=[12.5])  # Too few coordinates

    with pytest.raises(ValidationError):
        Point(coordinates=[12.5, 55.7, 100.0, 50.0])  # Too many coordinates


def test_multipoint_geometry_valid():
    """Test valid MultiPoint geometry."""
    multipoint = MultiPoint(coordinates=[[12.5, 55.7], [13.0, 56.0]])
    assert multipoint.type == "MultiPoint"
    assert len(multipoint.coordinates) == 2


def test_linestring_geometry_valid():
    """Test valid LineString geometry."""
    linestring = LineString(coordinates=[[12.5, 55.7], [13.0, 56.0]])
    assert linestring.type == "LineString"
    assert len(linestring.coordinates) == 2


def test_linestring_geometry_invalid_too_few_points():
    """Test LineString with too few points."""
    with pytest.raises(ValidationError):
        LineString(coordinates=[[12.5, 55.7]])  # Need at least 2 points


def test_polygon_geometry_valid():
    """Test valid Polygon geometry."""
    polygon = Polygon(
        coordinates=[
            [[12.5, 55.7], [13.0, 55.7], [13.0, 56.0], [12.5, 56.0], [12.5, 55.7]]
        ]
    )
    assert polygon.type == "Polygon"
    assert len(polygon.coordinates) == 1


def test_multipolygon_geometry_valid():
    """Test valid MultiPolygon geometry."""
    multipolygon = MultiPolygon(
        coordinates=[
            [[[12.5, 55.7], [13.0, 55.7], [13.0, 56.0], [12.5, 56.0], [12.5, 55.7]]]
        ]
    )
    assert multipolygon.type == "MultiPolygon"
    assert len(multipolygon.coordinates) == 1


def test_groundwater_station_properties_minimal():
    """Test station properties with minimal required fields."""
    props = GroundwaterStationProperties(row_id=123)
    assert props.row_id == 123
    assert props.station_id is None
    assert props.station_name is None


def test_groundwater_station_properties_full():
    """Test station properties with comprehensive fields."""
    props = GroundwaterStationProperties(
        row_id=123,
        station_id="95_2",
        station_name="Lagga_2",
        municipality="Linköping",
        reference_level=45.67,
        aquifer_code="K",
        aquifer_description="Kristallin grundvattenmagasin",
    )

    assert props.row_id == 123
    assert props.station_id == "95_2"
    assert props.station_name == "Lagga_2"
    assert props.reference_level == 45.67
    assert props.municipality == "Linköping"


def test_groundwater_station_properties_invalid_rowid():
    """Test station properties with invalid row_id."""
    with pytest.raises(ValidationError):
        GroundwaterStationProperties(row_id="invalid")


def test_groundwater_station_valid():
    """Test valid groundwater station."""
    station = GroundwaterStation(
        id="123",
        geometry=Point(coordinates=[15.5, 58.4]),
        properties=GroundwaterStationProperties(
            row_id=123, station_id="95_2", station_name="Test Station"
        ),
    )

    assert station.type == "Feature"
    assert station.id == "123"
    assert station.geometry.coordinates == [15.5, 58.4]
    assert station.properties.station_id == "95_2"


def test_groundwater_measurement_properties_minimal():
    """Test measurement properties with minimal fields."""
    props = GroundwaterMeasurementProperties(row_id=456, station_id="95_2")
    assert props.row_id == 456
    assert props.station_id == "95_2"
    assert props.observation_datetime is None


def test_groundwater_measurement_properties_with_date():
    """Test measurement properties with date parsing."""
    props = GroundwaterMeasurementProperties(
        row_id=456,
        station_id="95_2",
        observation_date="2023-06-15T10:30:00Z",
        water_level_masl_m=45.67,
        measurement_method="Tryckgivare",
    )

    assert props.row_id == 456
    assert props.observation_datetime == datetime(2023, 6, 15, 10, 30, 0, tzinfo=UTC)
    assert props.water_level_masl_m == 45.67


def test_groundwater_measurement_properties_invalid_date():
    """Test measurement properties with invalid date gracefully handled."""
    props = GroundwaterMeasurementProperties(
        row_id=456, station_id="95_2", observation_date="invalid-date"
    )
    assert props.observation_datetime is None


def test_groundwater_measurement_valid():
    """Test valid groundwater measurement."""
    measurement = GroundwaterMeasurement(
        id="456",
        geometry=Point(coordinates=[15.5, 58.4]),
        properties=GroundwaterMeasurementProperties(
            row_id=456,
            station_id="95_2",
            observation_date="2023-06-15T10:30:00Z",
            water_level_masl_m=45.67,
        ),
    )

    assert measurement.type == "Feature"
    assert measurement.id == "456"
    assert measurement.properties.observation_datetime.year == 2023


def test_crs_model():
    """Test CRS model."""
    crs = CRS(type="name", properties={"name": "EPSG:4326"})
    assert crs.type == "name"
    assert crs.properties["name"] == "EPSG:4326"


def test_link_model():
    """Test Link model."""
    link = Link(
        href="https://example.com/data", rel="self", type="application/geo+json"
    )
    assert link.href == "https://example.com/data"
    assert link.rel == "self"
    assert link.type == "application/geo+json"


def test_modeled_area_properties():
    """Test modeled area properties."""
    props = ModeledAreaProperties(
        omrade_id=100, url_tidsserie="https://api.sgu.se/timeseries/100"
    )
    assert props.omrade_id == 100
    assert props.url_tidsserie == "https://api.sgu.se/timeseries/100"


def test_modeled_area():
    """Test modeled area."""
    area = ModeledArea(
        id="area_100",
        geometry=Polygon(
            coordinates=[
                [
                    [12.5, 55.7],
                    [13.0, 55.7],
                    [13.0, 56.0],
                    [12.5, 56.0],
                    [12.5, 55.7],
                ]
            ]
        ),
        properties=ModeledAreaProperties(
            omrade_id=100, url_tidsserie="https://api.sgu.se/timeseries/100"
        ),
    )

    assert area.type == "Feature"
    assert area.id == "area_100"
    assert area.properties.omrade_id == 100


def test_modeled_groundwater_level_properties():
    """Test modeled groundwater level properties."""
    props = ModeledGroundwaterLevelProperties(
        omrade_id=100,
        objectid=1001,
        datum="2023-06-15",
        grundvattensituation_sma=25,
        grundvattensituation_stora=75,
        fyllnadsgrad_sma=30,
        fyllnadsgrad_stora=80,
    )

    assert props.omrade_id == 100
    assert props.objectid == 1001
    assert props.datum == "2023-06-15"
    assert props.grundvattensituation_sma == 25
    assert props.grundvattensituation_stora == 75


def test_modeled_groundwater_level_properties_percentile_validation():
    """Test percentile validation in modeled properties."""
    props = ModeledGroundwaterLevelProperties(
        omrade_id=100,
        objectid=1001,
        grundvattensituation_sma=0,
        grundvattensituation_stora=100,
        fyllnadsgrad_sma=0,
        fyllnadsgrad_stora=100,
    )
    assert props.grundvattensituation_sma == 0
    assert props.grundvattensituation_stora == 100


def test_modeled_groundwater_level():
    """Test modeled groundwater level."""
    level = ModeledGroundwaterLevel(
        id="level_100_20230615",
        geometry=Point(coordinates=[15.5, 58.4]),
        properties=ModeledGroundwaterLevelProperties(
            omrade_id=100,
            objectid=1001,
            datum="2023-06-15",
            grundvattensituation_sma=25,
            fyllnadsgrad_sma=30,
            fyllnadsgrad_stora=80,
        ),
    )

    assert level.type == "Feature"
    assert level.id == "level_100_20230615"
    assert level.properties.omrade_id == 100


def test_groundwater_station_collection():
    """Test groundwater station collection."""
    station = GroundwaterStation(
        id="123",
        geometry=Point(coordinates=[15.5, 58.4]),
        properties=GroundwaterStationProperties(row_id=123, station_id="95_2"),
    )

    collection = GroundwaterStationCollection(
        type="FeatureCollection",
        features=[station],
        numberReturned=1,
        numberMatched=1,
        totalFeatures=1,
        timeStamp="2024-01-01T00:00:00Z",
        links=[],
        crs={"type": "name", "properties": {"name": "EPSG:4326"}},
    )

    assert collection.type == "FeatureCollection"
    assert len(collection.features) == 1
    assert collection.numberReturned == 1
    assert collection.features[0].properties.station_id == "95_2"


def test_groundwater_measurement_collection():
    """Test groundwater measurement collection."""
    measurement = GroundwaterMeasurement(
        id="456",
        geometry=Point(coordinates=[15.5, 58.4]),
        properties=GroundwaterMeasurementProperties(
            row_id=456, station_id="95_2", observation_date="2023-06-15T10:30:00Z"
        ),
    )

    collection = GroundwaterMeasurementCollection(
        type="FeatureCollection",
        features=[measurement],
        numberReturned=1,
        totalFeatures=1,
        numberMatched=1,
        timeStamp="2024-01-01T00:00:00Z",
        links=[],
        crs={"type": "name", "properties": {"name": "EPSG:4326"}},
    )

    assert collection.type == "FeatureCollection"
    assert len(collection.features) == 1
    assert collection.features[0].properties.observation_date is not None


def test_geometry_with_invalid_coordinates():
    """Test geometry models with invalid coordinate types."""
    with pytest.raises(ValidationError):
        Point(coordinates=["invalid", "coordinates"])


def test_station_properties_with_none_values():
    """Test station properties with None values for optional fields."""
    props = GroundwaterStationProperties(
        row_id=123, station_id=None, station_name=None, reference_level=None
    )
    assert props.row_id == 123
    assert props.station_id is None
    assert props.reference_level is None


def test_collection_with_empty_features():
    """Test collection with empty features list."""
    collection = GroundwaterStationCollection(
        type="FeatureCollection",
        features=[],
        numberReturned=0,
        totalFeatures=0,
        numberMatched=0,
        timeStamp="2024-01-01T00:00:00Z",
        links=[],
        crs={"type": "name", "properties": {"name": "EPSG:4326"}},
    )
    assert len(collection.features) == 0
    assert collection.numberReturned == 0


def test_model_dump_uses_english_field_names():
    """Test that model_dump uses English field names."""
    props = GroundwaterStationProperties(
        row_id=123, station_id="95_2", station_name="Test Station"
    )

    data = props.model_dump()
    assert "station_id" in data
    assert "station_name" in data
    assert data["station_id"] == "95_2"
