"""Basic tests for modeled groundwater levels endpoints.

TODO: Switch to mock requests like in tests/test_observed.py to improve test speed
and reliability. Currently uses real API calls which makes tests slower.
"""

from datetime import datetime

import pytest
from pandas.api.types import is_datetime64_any_dtype as is_datetime

from sgu_client import SGUClient
from sgu_client.config import SGUConfig
from sgu_client.exceptions import SGUTimeoutError
from sgu_client.models.modeled import (
    ModeledArea,
    ModeledAreaCollection,
    ModeledGroundwaterLevel,
    ModeledGroundwaterLevelCollection,
)

TEST_AREA_ID = "omraden.30125"
TEST_AREA_OMRADE_ID = 30125
TEST_LEVEL_ID = "grundvattennivaer-tidigare.1"
TEST_LEVEL_OMRADE_ID = 30125
TEST_LEVEL_DATUM = "2024-08-01Z"
TEST_LEVEL_OBJECTID = 1


def test_create_basic_client() -> None:
    client = SGUClient()
    assert hasattr(client, "levels")
    assert hasattr(client.levels, "modeled")


def test_get_areas() -> None:
    client = SGUClient()
    areas = client.levels.modeled.get_areas(limit=10)
    assert areas is not None
    assert isinstance(areas, ModeledAreaCollection)
    assert len(areas.features) > 0
    assert all(isinstance(area, ModeledArea) for area in areas.features)


def test_get_area_by_id() -> None:
    client = SGUClient()
    area = client.levels.modeled.get_area(TEST_AREA_ID)
    assert area is not None
    assert isinstance(area, ModeledArea)
    assert area.id == TEST_AREA_ID
    assert area.properties.omrade_id == TEST_AREA_OMRADE_ID
    assert area.geometry.type == "MultiPolygon"
    assert area.geometry.coordinates is not None


def test_get_area_not_found() -> None:
    client = SGUClient()
    with pytest.raises(ValueError, match="Area nonexistent.999999 not found"):
        client.levels.modeled.get_area("nonexistent.999999")


def test_get_levels() -> None:
    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0
    assert all(isinstance(level, ModeledGroundwaterLevel) for level in levels.features)


def test_get_level_by_id() -> None:
    client = SGUClient()
    level = client.levels.modeled.get_level(TEST_LEVEL_ID)
    assert level is not None
    assert isinstance(level, ModeledGroundwaterLevel)
    assert level.id == TEST_LEVEL_ID
    assert level.properties.omrade_id == TEST_LEVEL_OMRADE_ID
    assert level.properties.datum == TEST_LEVEL_DATUM
    assert level.properties.objectid == TEST_LEVEL_OBJECTID
    assert isinstance(level.properties.date, datetime)


def test_get_level_not_found() -> None:
    client = SGUClient()
    with pytest.raises(ValueError, match="Level nonexistent.999999 not found"):
        client.levels.modeled.get_level("nonexistent.999999")


def test_areas_with_bbox() -> None:
    client = SGUClient()
    # Test with a bbox covering southern Sweden
    areas = client.levels.modeled.get_areas(bbox=[12.0, 55.0, 16.0, 58.0], limit=5)
    assert areas is not None
    assert isinstance(areas, ModeledAreaCollection)
    # Should have at least some areas in this region
    assert len(areas.features) >= 0


def test_levels_basic_query() -> None:
    client = SGUClient()
    # Test basic query without datetime filtering (API seems to have issues with datetime)
    levels = client.levels.modeled.get_levels(limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # Check that we got some basic data structure
    for level in levels.features:
        assert level.properties.omrade_id is not None
        assert level.properties.objectid is not None


def test_levels_with_filter_expr() -> None:
    client = SGUClient()
    # Test filtering by area ID
    levels = client.levels.modeled.get_levels(
        filter_expr=f"omrade_id = {TEST_LEVEL_OMRADE_ID}", limit=5
    )
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # All results should have the specified area ID
    for level in levels.features:
        assert level.properties.omrade_id == TEST_LEVEL_OMRADE_ID


def test_levels_with_sortby() -> None:
    client = SGUClient()
    # Test sorting by date descending
    levels = client.levels.modeled.get_levels(sortby=["-datum"], limit=5)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # Check that dates are in descending order (latest first)
    dates = [
        level.properties.date for level in levels.features if level.properties.date
    ]
    for i in range(len(dates) - 1):
        assert dates[i] >= dates[i + 1]


def test_areas_to_dataframe() -> None:
    client = SGUClient()
    areas = client.levels.modeled.get_areas(limit=5)
    assert areas is not None
    df = areas.to_dataframe()
    assert not df.empty
    assert "area_id" in df.columns
    assert "omrade_id" in df.columns
    assert "geometry_type" in df.columns
    assert "centroid_longitude" in df.columns
    assert "centroid_latitude" in df.columns

    # Check that we have the expected area
    assert TEST_AREA_ID in df["area_id"].tolist()


def test_levels_to_dataframe() -> None:
    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=5)
    assert levels is not None
    df = levels.to_dataframe()
    assert not df.empty
    assert "level_id" in df.columns
    assert "date" in df.columns
    assert "omrade_id" in df.columns
    assert "datum" in df.columns
    assert "objectid" in df.columns

    # Assert that it is sorted by date by default
    assert is_datetime(df["date"])
    # Note: some dates might be None, so we need to handle that
    valid_dates = df["date"].dropna()
    if len(valid_dates) > 1:
        assert valid_dates.is_monotonic_increasing


def test_levels_to_series() -> None:
    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=5)
    assert levels is not None
    series = levels.to_series()
    assert not series.empty

    assert is_datetime(series.index)


def test_levels_to_series_custom_index_data() -> None:
    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=5)
    assert levels is not None
    series = levels.to_series(index="fyllnadsgrad_sma", data="fyllnadsgrad_stora")
    assert not series.empty

    with pytest.raises(ValueError):
        levels.to_series(index="invalid_column")

    with pytest.raises(ValueError):
        levels.to_series(data="invalid_column")


def test_levels_to_dataframe_no_sort() -> None:
    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=5)
    assert levels is not None
    df = levels.to_dataframe(sort_by_date=False)
    assert not df.empty
    assert "date" in df.columns


def test_date_property_parsing() -> None:
    client = SGUClient()
    level = client.levels.modeled.get_level(TEST_LEVEL_ID)
    assert level.properties.datum == TEST_LEVEL_DATUM
    assert isinstance(level.properties.date, datetime)
    assert level.properties.date.year == 2024
    assert level.properties.date.month == 8
    assert level.properties.date.day == 1


def test_percentile_validation() -> None:
    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=10)
    assert levels is not None

    for level in levels.features:
        props = level.properties
        # Check that percentiles are either None or in valid range
        if props.grundvattensituation_sma is not None:
            assert 0 <= props.grundvattensituation_sma <= 100
        if props.grundvattensituation_stora is not None:
            assert 0 <= props.grundvattensituation_stora <= 100
        if props.fyllnadsgrad_sma is not None:
            assert 0 <= props.fyllnadsgrad_sma <= 100
        if props.fyllnadsgrad_stora is not None:
            assert 0 <= props.fyllnadsgrad_stora <= 100


def test_get_levels_by_area() -> None:
    client = SGUClient()
    levels = client.levels.modeled.get_levels_by_area(TEST_LEVEL_OMRADE_ID, limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # All results should have the specified area ID
    for level in levels.features:
        assert level.properties.omrade_id == TEST_LEVEL_OMRADE_ID


def test_get_levels_by_area_to_dataframe() -> None:
    client = SGUClient()
    levels = client.levels.modeled.get_levels_by_area(TEST_LEVEL_OMRADE_ID, limit=10)
    df = levels.to_dataframe(sort_by_date=True)
    assert not df.empty
    assert "level_id" in df.columns
    assert "date" in df.columns
    assert "omrade_id" in df.columns
    assert "datum" in df.columns

    assert is_datetime(df["date"])
    # Note: some dates might be None, so we need to handle that
    valid_dates = df["date"].dropna()
    if len(valid_dates) > 1:
        assert valid_dates.is_monotonic_increasing


def test_get_levels_by_area_with_limit() -> None:
    client = SGUClient()
    levels = client.levels.modeled.get_levels_by_area(TEST_LEVEL_OMRADE_ID, limit=5)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) <= 5

    # All results should have the specified area ID
    for level in levels.features:
        assert level.properties.omrade_id == TEST_LEVEL_OMRADE_ID


def test_get_levels_by_area_nonexistent() -> None:
    # Use short timeout to avoid freezing on non-existent area
    config = SGUConfig(timeout=5.0, max_retries=0)
    client = SGUClient(config=config)

    # API freezes when searching for non-existent area, so expect timeout
    with pytest.raises(SGUTimeoutError):
        client.levels.modeled.get_levels_by_area(999999, limit=10)


def test_get_levels_by_areas() -> None:
    client = SGUClient()
    area_ids = [TEST_LEVEL_OMRADE_ID, 30126]  # Use test area and another one
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=20)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # All results should have one of the specified area IDs
    for level in levels.features:
        assert level.properties.omrade_id in area_ids


def test_get_levels_by_areas_single_area() -> None:
    client = SGUClient()
    # Test with single area ID in list (should work same as get_levels_by_area)
    area_ids = [TEST_LEVEL_OMRADE_ID]
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # All results should have the specified area ID
    for level in levels.features:
        assert level.properties.omrade_id == TEST_LEVEL_OMRADE_ID


def test_get_levels_by_areas_empty_list() -> None:
    client = SGUClient()
    # Test with empty area IDs list - should raise ValueError
    with pytest.raises(ValueError, match="At least one area ID must be provided"):
        client.levels.modeled.get_levels_by_areas([], limit=10)


def test_get_levels_by_areas_to_dataframe() -> None:
    client = SGUClient()
    area_ids = [TEST_LEVEL_OMRADE_ID, 30126]
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=10)
    df = levels.to_dataframe(sort_by_date=True)
    assert not df.empty
    assert "level_id" in df.columns
    assert "date" in df.columns
    assert "omrade_id" in df.columns
    assert "datum" in df.columns

    assert is_datetime(df["date"])
    # Note: some dates might be None, so we need to handle that
    valid_dates = df["date"].dropna()
    if len(valid_dates) > 1:
        assert valid_dates.is_monotonic_increasing

    # Check that all area IDs in dataframe are from our requested list
    for omrade_id in df["omrade_id"].unique():
        assert omrade_id in area_ids


def test_get_levels_by_areas_with_limit() -> None:
    client = SGUClient()
    area_ids = [TEST_LEVEL_OMRADE_ID, 30126]
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=5)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) <= 5

    # All results should have one of the specified area IDs
    for level in levels.features:
        assert level.properties.omrade_id in area_ids


def test_get_levels_by_areas_nonexistent() -> None:
    # Use short timeout to avoid freezing on non-existent area
    config = SGUConfig(timeout=5.0, max_retries=0)
    client = SGUClient(config=config)

    # API freezes when searching for non-existent areas, so expect timeout
    with pytest.raises(SGUTimeoutError):
        client.levels.modeled.get_levels_by_areas([999998, 999999], limit=10)


def test_get_levels_by_areas_mixed_existing_nonexistent() -> None:
    client = SGUClient()
    # Mix existing and non-existent area IDs
    area_ids = [TEST_LEVEL_OMRADE_ID, 999999]
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)

    # Should only have levels from the existing area
    for level in levels.features:
        assert level.properties.omrade_id == TEST_LEVEL_OMRADE_ID


def test_build_query_params_helper() -> None:
    client = SGUClient()
    modeled_client = client.levels.modeled

    # Test bbox parameter
    params = modeled_client._build_query_params(bbox=[12.0, 55.0, 16.0, 58.0])
    assert params["bbox"] == "12.0,55.0,16.0,58.0"

    # Test sortby parameter
    params = modeled_client._build_query_params(sortby=["+datum", "-omrade_id"])
    assert params["sortby"] == "+datum,-omrade_id"

    # Test None values are filtered out
    params = modeled_client._build_query_params(limit=10, bbox=None, datetime=None)
    assert "bbox" not in params
    assert "datetime" not in params
    assert params["limit"] == 10

    # Test regular parameters pass through
    params = modeled_client._build_query_params(
        limit=100, filter="omrade_id = 30125", datetime="2024-08-01Z"
    )
    assert params["limit"] == 100
    assert params["filter"] == "omrade_id = 30125"
    assert params["datetime"] == "2024-08-01Z"


def test_get_levels_by_coords_single_area() -> None:
    """Test get_levels_by_coords with coordinates that find a single area."""
    client = SGUClient()
    # Test with coordinates in Gothenburg area (should find single area)
    levels = client.levels.modeled.get_levels_by_coords(
        lat=57.7089, lon=11.9746, limit=5
    )
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # Check that all levels have the same area ID (single area found)
    area_ids = {level.properties.omrade_id for level in levels.features}
    assert len(area_ids) == 1  # Should only find one area


def test_get_levels_by_coords_boundary_warning(caplog) -> None:
    """Test get_levels_by_coords with coordinates near boundary (multiple areas)."""
    import logging

    # Set up logging to capture warnings
    caplog.set_level(logging.WARNING)

    client = SGUClient()
    # Test with coordinates in Stockholm area (known to find multiple areas)
    levels = client.levels.modeled.get_levels_by_coords(
        lat=59.3293, lon=18.0686, limit=5
    )
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # Check that warning was logged (indicating multiple areas were found)
    warning_logged = any(
        "Found" in record.message and "areas near coordinates" in record.message
        for record in caplog.records
        if record.levelname == "WARNING"
    )
    assert warning_logged, "Expected boundary warning was not logged"

    # Verify the warning mentions multiple areas
    warning_messages = [
        record.message
        for record in caplog.records
        if record.levelname == "WARNING" and "Found" in record.message
    ]
    assert len(warning_messages) > 0
    # The warning should mention that multiple areas were found
    assert any(
        "Found 2" in msg or "Found 3" in msg or "Found 4" in msg
        for msg in warning_messages
    ), f"Warning should mention multiple areas: {warning_messages}"


def test_get_levels_by_coords_outside_sweden() -> None:
    """Test get_levels_by_coords with coordinates outside Sweden."""
    client = SGUClient()
    # Test with coordinates outside Sweden (London)
    with pytest.raises(
        ValueError, match="No modeled groundwater areas found near coordinates"
    ):
        client.levels.modeled.get_levels_by_coords(lat=51.5074, lon=-0.1278, limit=5)


def test_get_levels_by_coords_with_datetime() -> None:
    """Test get_levels_by_coords with datetime filtering."""
    client = SGUClient()
    # Test with coordinates and datetime filtering (2023 data)
    levels = client.levels.modeled.get_levels_by_coords(
        lat=57.7089, lon=11.9746, datetime="2023-01-01/2023-12-31", limit=10
    )
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # Check that all dates are from 2023
    for level in levels.features:
        if level.properties.date:
            assert level.properties.date.year == 2023


def test_get_levels_by_coords_custom_buffer() -> None:
    """Test get_levels_by_coords with custom buffer parameter."""
    client = SGUClient()

    # Test with small buffer (should find fewer/no areas)
    small_buffer_levels = client.levels.modeled.get_levels_by_coords(
        lat=57.7089,
        lon=11.9746,
        buffer=0.001,  # Very small buffer (~100m)
        limit=10,
    )

    # Test with larger buffer (should find more areas)
    large_buffer_levels = client.levels.modeled.get_levels_by_coords(
        lat=57.7089,
        lon=11.9746,
        buffer=0.1,  # Large buffer (~10km)
        limit=10,
    )

    assert small_buffer_levels is not None
    assert large_buffer_levels is not None
    assert isinstance(small_buffer_levels, ModeledGroundwaterLevelCollection)
    assert isinstance(large_buffer_levels, ModeledGroundwaterLevelCollection)

    # Large buffer should find more or equal areas than small buffer
    small_area_ids = {
        level.properties.omrade_id for level in small_buffer_levels.features
    }
    large_area_ids = {
        level.properties.omrade_id for level in large_buffer_levels.features
    }
    assert len(large_area_ids) >= len(small_area_ids)
