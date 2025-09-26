"""Tests for modeled groundwater levels endpoints using mocked API responses.

These tests use mocked HTTP responses to ensure fast, reliable testing without
depending on external API availability. For integration tests that verify the
real API still works, see test_actual_api.py.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from requests import Response

from sgu_client import SGUClient
from sgu_client.exceptions import SGUAPIError, SGUConnectionError, SGUTimeoutError
from sgu_client.models.modeled import (
    ModeledArea,
    ModeledAreaCollection,
    ModeledGroundwaterLevel,
    ModeledGroundwaterLevelCollection,
)
from tests.mock_responses import (
    create_mock_empty_modeled_collection_response,
    create_mock_multiple_modeled_areas_response,
    create_mock_multiple_modeled_levels_response,
    create_mock_single_modeled_area_response,
    create_mock_single_modeled_level_response,
)

# Test constants
TEST_AREA_ID = "omraden.30125"
TEST_AREA_OMRADE_ID = 30125
TEST_LEVEL_ID = "grundvattennivaer-tidigare.1"
TEST_LEVEL_OMRADE_ID = 30125
TEST_LEVEL_DATUM = "2024-08-01Z"
TEST_LEVEL_OBJECTID = 1


def create_mock_response(response_data, status_code=200):
    """Create a mock HTTP response object."""
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = status_code
    mock_response.json.return_value = response_data
    return mock_response


def test_create_basic_client() -> None:
    client = SGUClient()
    assert hasattr(client, "levels")
    assert hasattr(client.levels, "modeled")


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_areas(mock_request) -> None:
    """Test getting modeled areas with mocked response."""
    mock_response_data = create_mock_multiple_modeled_areas_response(
        area_ids=[30125, 30126], limit=10
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    areas = client.levels.modeled.get_areas(limit=10)
    assert areas is not None
    assert isinstance(areas, ModeledAreaCollection)
    assert len(areas.features) > 0
    assert all(isinstance(area, ModeledArea) for area in areas.features)


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_area_by_id(mock_request) -> None:
    """Test getting a specific area by ID with mocked response."""
    mock_response_data = create_mock_single_modeled_area_response(
        area_id=TEST_AREA_ID, omrade_id=TEST_AREA_OMRADE_ID
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    area = client.levels.modeled.get_area(TEST_AREA_ID)
    assert area is not None
    assert isinstance(area, ModeledArea)
    assert area.id == TEST_AREA_ID
    assert area.properties.area_id == TEST_AREA_OMRADE_ID
    assert area.geometry.type == "MultiPolygon"
    assert area.geometry.coordinates is not None


def test_get_area_not_found() -> None:
    """Test handling of non-existent area requests."""
    with patch("requests.Session.request") as mock_request:
        mock_response_data = create_mock_empty_modeled_collection_response()
        mock_request.return_value = create_mock_response(mock_response_data)

        client = SGUClient()
        with pytest.raises(ValueError, match="Area .* not found"):
            client.levels.modeled.get_area("nonexistent.999999")


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels(mock_request) -> None:
    """Test getting modeled levels with mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0
    assert all(isinstance(level, ModeledGroundwaterLevel) for level in levels.features)


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_level_by_id(mock_request) -> None:
    """Test getting a specific level by ID with mocked response."""
    mock_response_data = create_mock_single_modeled_level_response(
        level_id=TEST_LEVEL_ID,
        omrade_id=TEST_LEVEL_OMRADE_ID,
        datum=TEST_LEVEL_DATUM,
        objectid=TEST_LEVEL_OBJECTID,
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    level = client.levels.modeled.get_level(TEST_LEVEL_ID)
    assert level is not None
    assert isinstance(level, ModeledGroundwaterLevel)
    assert level.id == TEST_LEVEL_ID
    assert level.properties.area_id == TEST_LEVEL_OMRADE_ID
    assert level.properties.date == TEST_LEVEL_DATUM
    assert level.properties.object_id == TEST_LEVEL_OBJECTID
    assert isinstance(level.properties.date_parsed, datetime)


def test_get_level_not_found() -> None:
    """Test handling of non-existent level requests."""
    with patch("requests.Session.request") as mock_request:
        mock_response_data = create_mock_empty_modeled_collection_response()
        mock_request.return_value = create_mock_response(mock_response_data)

        client = SGUClient()
        with pytest.raises(ValueError, match="Level .* not found"):
            client.levels.modeled.get_level("nonexistent.999999")


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_areas_with_bbox(mock_request) -> None:
    """Test getting areas with bbox filter using mocked response."""
    mock_response_data = create_mock_multiple_modeled_areas_response(
        area_ids=[30125, 30126], limit=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    # Test with a bbox covering southern Sweden
    areas = client.levels.modeled.get_areas(bbox=[12.0, 55.0, 16.0, 58.0], limit=5)
    assert areas is not None
    assert isinstance(areas, ModeledAreaCollection)
    # Should have at least some areas in this region
    assert len(areas.features) >= 0


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_levels_basic_query(mock_request) -> None:
    """Test basic levels query with mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    # Test basic query without datetime filtering (API seems to have issues with datetime)
    levels = client.levels.modeled.get_levels(limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # Check that we got some basic data structure
    for level in levels.features:
        assert level.properties.area_id is not None
        assert level.properties.object_id is not None


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_levels_with_filter_expr(mock_request) -> None:
    """Test levels query with filter expression using mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=3
    )
    mock_request.return_value = create_mock_response(mock_response_data)

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
        assert level.properties.area_id == TEST_LEVEL_OMRADE_ID


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_levels_with_sortby(mock_request) -> None:
    """Test levels query with sorting using mocked response."""
    # Create levels with descending dates
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=3
    )
    # Reverse the order to simulate descending sort
    mock_response_data["features"].reverse()
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    # Test sorting by date descending
    levels = client.levels.modeled.get_levels(sortby=["-datum"], limit=5)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # Check that dates are in descending order (latest first)
    dates = [
        level.properties.date_parsed
        for level in levels.features
        if level.properties.date_parsed
    ]
    for i in range(len(dates) - 1):
        assert dates[i] >= dates[i + 1]


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_areas_to_dataframe(mock_request) -> None:
    """Test converting areas to DataFrame with mocked response."""
    mock_response_data = create_mock_multiple_modeled_areas_response(
        area_ids=[TEST_AREA_OMRADE_ID, 30126], limit=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    areas = client.levels.modeled.get_areas(limit=5)
    assert areas is not None
    df = areas.to_dataframe()
    assert not df.empty
    assert "feature_id" in df.columns
    assert "area_id" in df.columns
    assert "geometry_type" in df.columns
    assert "centroid_longitude" in df.columns
    assert "centroid_latitude" in df.columns

    # Check that we have the expected area
    assert TEST_AREA_ID in df["feature_id"].tolist()


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_levels_to_dataframe(mock_request) -> None:
    """Test converting levels to DataFrame with mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=5)
    assert levels is not None
    df = levels.to_dataframe()
    assert not df.empty
    assert "level_id" in df.columns
    assert "date" in df.columns
    assert "area_id" in df.columns
    assert "date" in df.columns
    assert "object_id" in df.columns

    # Assert that it is sorted by date by default
    assert is_datetime(df["date"])
    # Note: some dates might be None, so we need to handle that
    valid_dates = df["date"].dropna()
    if len(valid_dates) > 1:
        assert valid_dates.is_monotonic_increasing


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_levels_to_series(mock_request) -> None:
    """Test converting levels to Series with mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=5)
    assert levels is not None
    series = levels.to_series()
    assert not series.empty

    assert is_datetime(series.index)


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_levels_to_series_custom_index_data(mock_request) -> None:
    """Test converting levels to Series with custom index/data columns using mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=5)
    assert levels is not None
    series = levels.to_series(
        index="relative_level_small_resources", data="relative_level_large_resources"
    )
    assert not series.empty

    with pytest.raises(ValueError):
        levels.to_series(index="invalid_column")

    with pytest.raises(ValueError):
        levels.to_series(data="invalid_column")


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_levels_to_dataframe_no_sort(mock_request) -> None:
    """Test converting levels to DataFrame without sorting using mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=5)
    assert levels is not None
    df = levels.to_dataframe(sort_by_date=False)
    assert not df.empty
    assert "date" in df.columns


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_date_property_parsing(mock_request) -> None:
    """Test date property parsing with mocked response."""
    mock_response_data = create_mock_single_modeled_level_response(
        level_id=TEST_LEVEL_ID,
        omrade_id=TEST_LEVEL_OMRADE_ID,
        datum=TEST_LEVEL_DATUM,
        objectid=TEST_LEVEL_OBJECTID,
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    level = client.levels.modeled.get_level(TEST_LEVEL_ID)
    assert level.properties.date == TEST_LEVEL_DATUM
    assert isinstance(level.properties.date_parsed, datetime)
    assert level.properties.date_parsed.year == 2024
    assert level.properties.date_parsed.month == 8
    assert level.properties.date_parsed.day == 1


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_percentile_validation(mock_request) -> None:
    """Test percentile value validation with mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels(limit=10)
    assert levels is not None

    for level in levels.features:
        props = level.properties
        # Check that percentiles are either None or in valid range
        if props.deviation_small_resources is not None:
            assert 0 <= props.deviation_small_resources <= 100
        if props.deviation_large_resources is not None:
            assert 0 <= props.deviation_large_resources <= 100
        if props.relative_level_small_resources is not None:
            assert 0 <= props.relative_level_small_resources <= 100
        if props.relative_level_large_resources is not None:
            assert 0 <= props.relative_level_large_resources <= 100


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_area(mock_request) -> None:
    """Test getting levels by area ID with mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels_by_area(TEST_LEVEL_OMRADE_ID, limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # All results should have the specified area ID
    for level in levels.features:
        assert level.properties.area_id == TEST_LEVEL_OMRADE_ID


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_area_to_dataframe(mock_request) -> None:
    """Test converting levels by area to DataFrame with mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels_by_area(TEST_LEVEL_OMRADE_ID, limit=10)
    df = levels.to_dataframe(sort_by_date=True)
    assert not df.empty
    assert "level_id" in df.columns
    assert "date" in df.columns
    assert "area_id" in df.columns
    assert "date" in df.columns

    assert is_datetime(df["date"])
    # Note: some dates might be None, so we need to handle that
    valid_dates = df["date"].dropna()
    if len(valid_dates) > 1:
        assert valid_dates.is_monotonic_increasing


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_area_with_limit(mock_request) -> None:
    """Test getting levels by area with limit using mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=3
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels_by_area(TEST_LEVEL_OMRADE_ID, limit=5)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) <= 5

    # All results should have the specified area ID
    for level in levels.features:
        assert level.properties.area_id == TEST_LEVEL_OMRADE_ID


def test_get_levels_by_area_nonexistent() -> None:
    """Test timeout error for non-existent area using mocked response."""
    import requests.exceptions

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = requests.exceptions.ReadTimeout("Read timeout")

        client = SGUClient()
        # API freezes when searching for non-existent area, so expect timeout
        with pytest.raises(SGUTimeoutError):
            client.levels.modeled.get_levels_by_area(999999, limit=10)


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_areas(mock_request) -> None:
    """Test getting levels by multiple area IDs with mocked response."""
    area_ids = [TEST_LEVEL_OMRADE_ID, 30126]
    # Create levels for both areas
    levels_30125 = create_mock_multiple_modeled_levels_response(
        omrade_id=30125, count=3
    )["features"]
    levels_30126 = create_mock_multiple_modeled_levels_response(
        omrade_id=30126, count=2
    )["features"]

    # Update area IDs for second set
    for level in levels_30126:
        level["properties"]["omrade_id"] = 30126

    all_levels = levels_30125 + levels_30126
    mock_response_data = create_mock_multiple_modeled_levels_response(count=0)
    mock_response_data["features"] = all_levels
    mock_response_data["numberReturned"] = len(all_levels)
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=20)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # All results should have one of the specified area IDs
    for level in levels.features:
        assert level.properties.area_id in area_ids


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_areas_single_area(mock_request) -> None:
    """Test getting levels by single area ID in list with mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    # Test with single area ID in list (should work same as get_levels_by_area)
    area_ids = [TEST_LEVEL_OMRADE_ID]
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # All results should have the specified area ID
    for level in levels.features:
        assert level.properties.area_id == TEST_LEVEL_OMRADE_ID


def test_get_levels_by_areas_empty_list() -> None:
    client = SGUClient()
    # Test with empty area IDs list - should raise ValueError
    with pytest.raises(ValueError, match="At least one area ID must be provided"):
        client.levels.modeled.get_levels_by_areas([], limit=10)


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_areas_to_dataframe(mock_request) -> None:
    """Test converting levels by multiple areas to DataFrame with mocked response."""
    area_ids = [TEST_LEVEL_OMRADE_ID, 30126]
    # Create combined response
    levels_30125 = create_mock_multiple_modeled_levels_response(
        omrade_id=30125, count=3
    )["features"]
    levels_30126 = create_mock_multiple_modeled_levels_response(
        omrade_id=30126, count=2
    )["features"]

    # Update area IDs for second set
    for level in levels_30126:
        level["properties"]["omrade_id"] = 30126

    all_levels = levels_30125 + levels_30126
    mock_response_data = create_mock_multiple_modeled_levels_response(count=0)
    mock_response_data["features"] = all_levels
    mock_response_data["numberReturned"] = len(all_levels)
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=10)
    df = levels.to_dataframe(sort_by_date=True)
    assert not df.empty
    assert "level_id" in df.columns
    assert "date" in df.columns
    assert "area_id" in df.columns
    assert "date" in df.columns

    assert is_datetime(df["date"])
    # Note: some dates might be None, so we need to handle that
    valid_dates = df["date"].dropna()
    if len(valid_dates) > 1:
        assert valid_dates.is_monotonic_increasing

    # Check that all area IDs in dataframe are from our requested list
    for area_id in df["area_id"].unique():
        assert area_id in area_ids


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_areas_with_limit(mock_request) -> None:
    """Test getting levels by multiple areas with limit using mocked response."""
    area_ids = [TEST_LEVEL_OMRADE_ID, 30126]
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=3
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=5)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) <= 5

    # All results should have one of the specified area IDs
    for level in levels.features:
        assert level.properties.area_id in area_ids


def test_get_levels_by_areas_nonexistent() -> None:
    """Test timeout error for non-existent areas using mocked response."""
    import requests.exceptions

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = requests.exceptions.ReadTimeout("Read timeout")

        client = SGUClient()
        # API freezes when searching for non-existent areas, so expect timeout
        with pytest.raises(SGUTimeoutError):
            client.levels.modeled.get_levels_by_areas([999998, 999999], limit=10)


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_areas_mixed_existing_nonexistent(mock_request) -> None:
    """Test mixed existing/non-existent area IDs with mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    # Mix existing and non-existent area IDs
    area_ids = [TEST_LEVEL_OMRADE_ID, 999999]
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)

    # Should only have levels from the existing area
    for level in levels.features:
        assert level.properties.area_id == TEST_LEVEL_OMRADE_ID


def test_build_query_params_helper() -> None:
    """Test the internal query parameter building helper function."""
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


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_coords_single_area(mock_request) -> None:
    """Test get_levels_by_coords with coordinates that find a single area using mocked response."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    mock_request.return_value = create_mock_response(mock_response_data)

    client = SGUClient()
    # Test with coordinates in Gothenburg area (should find single area)
    levels = client.levels.modeled.get_levels_by_coords(
        lat=57.7089, lon=11.9746, limit=5
    )
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # Check that all levels have the same area ID (single area found)
    area_ids = {level.properties.area_id for level in levels.features}
    assert len(area_ids) == 1  # Should only find one area


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_coords_boundary_warning(mock_request, caplog) -> None:
    """Test get_levels_by_coords with coordinates near boundary (multiple areas) using mocked response."""
    import logging

    # Set up logging to capture warnings
    caplog.set_level(logging.WARNING)

    # Create levels from multiple areas to simulate boundary case
    levels_30125 = create_mock_multiple_modeled_levels_response(
        omrade_id=30125, count=2
    )["features"]
    levels_30126 = create_mock_multiple_modeled_levels_response(
        omrade_id=30126, count=3
    )["features"]

    # Update area IDs for second set
    for level in levels_30126:
        level["properties"]["omrade_id"] = 30126

    all_levels = levels_30125 + levels_30126
    mock_response_data = create_mock_multiple_modeled_levels_response(count=0)
    mock_response_data["features"] = all_levels
    mock_response_data["numberReturned"] = len(all_levels)
    mock_request.return_value = create_mock_response(mock_response_data)

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
    """Test get_levels_by_coords with coordinates outside Sweden using mocked response."""
    with patch("requests.Session.request") as mock_request:
        mock_response_data = create_mock_empty_modeled_collection_response()
        mock_request.return_value = create_mock_response(mock_response_data)

        client = SGUClient()
        # Test with coordinates outside Sweden (London)
        with pytest.raises(
            ValueError, match="No modeled groundwater areas found near coordinates"
        ):
            client.levels.modeled.get_levels_by_coords(
                lat=51.5074, lon=-0.1278, limit=5
            )


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_coords_with_datetime(mock_request) -> None:
    """Test get_levels_by_coords with datetime filtering using mocked response."""
    from datetime import UTC, datetime

    # Create 2023 data
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID,
        count=3,
        start_date=datetime(2023, 1, 1, tzinfo=UTC),
    )
    mock_request.return_value = create_mock_response(mock_response_data)

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
        if level.properties.date_parsed:
            assert level.properties.date_parsed.year == 2023


@patch.object(SGUClient().levels.modeled._client._session, "request")
def test_get_levels_by_coords_custom_buffer(mock_request) -> None:
    """Test get_levels_by_coords with custom buffer parameter using mocked response."""

    def mock_request_side_effect(*args, **kwargs):
        # Return fewer areas for small buffer, more for large buffer
        if "buffer=0.001" in str(kwargs) or (
            len(args) > 1 and "buffer=0.001" in str(args[1])
        ):
            # Small buffer - fewer results
            data = create_mock_multiple_modeled_levels_response(
                omrade_id=TEST_LEVEL_OMRADE_ID, count=2
            )
        else:
            # Large buffer - more results
            data = create_mock_multiple_modeled_levels_response(
                omrade_id=TEST_LEVEL_OMRADE_ID, count=5
            )
        return create_mock_response(data)

    mock_request.side_effect = mock_request_side_effect

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
        level.properties.area_id for level in small_buffer_levels.features
    }
    large_area_ids = {
        level.properties.area_id for level in large_buffer_levels.features
    }
    assert len(large_area_ids) >= len(small_area_ids)


# Comprehensive error condition tests (enabled by mocking)
def test_api_timeout_error() -> None:
    """Test that API timeout errors are properly raised."""
    import requests.exceptions

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = requests.exceptions.ReadTimeout("Read timeout")

        client = SGUClient()
        with pytest.raises(SGUTimeoutError, match="Read timeout"):
            client.levels.modeled.get_area(TEST_AREA_ID)


def test_api_connection_error() -> None:
    """Test that API connection errors are properly raised."""
    import requests.exceptions

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        client = SGUClient()
        with pytest.raises(SGUConnectionError, match="Connection failed"):
            client.levels.modeled.get_area(TEST_AREA_ID)


def test_api_server_error() -> None:
    """Test that API server errors are properly raised."""
    with patch("requests.Session.request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_request.return_value = mock_response

        client = SGUClient()
        with pytest.raises(SGUAPIError, match="API request failed with status 500"):
            client.levels.modeled.get_area(TEST_AREA_ID)


def test_api_not_found_error() -> None:
    """Test that API 404 errors are properly raised."""
    with patch("requests.Session.request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Area not found"}
        mock_request.return_value = mock_response

        client = SGUClient()
        with pytest.raises(SGUAPIError, match="API request failed with status 404"):
            client.levels.modeled.get_area("nonexistent.area")


def test_empty_area_response_handling() -> None:
    """Test handling of empty area responses."""
    with patch("requests.Session.request") as mock_request:
        mock_response_data = create_mock_empty_modeled_collection_response()
        mock_request.return_value = create_mock_response(mock_response_data)

        client = SGUClient()
        with pytest.raises(ValueError, match="Area .* not found"):
            client.levels.modeled.get_area("nonexistent.area")


def test_empty_level_response_handling() -> None:
    """Test handling of empty level responses."""
    with patch("requests.Session.request") as mock_request:
        mock_response_data = create_mock_empty_modeled_collection_response()
        mock_request.return_value = create_mock_response(mock_response_data)

        client = SGUClient()
        with pytest.raises(ValueError, match="Level .* not found"):
            client.levels.modeled.get_level("nonexistent.level")


def test_malformed_json_response() -> None:
    """Test handling of malformed JSON responses."""
    with patch("requests.Session.request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Internal Server Error - HTML response"
        mock_request.return_value = mock_response

        client = SGUClient()
        with pytest.raises(SGUAPIError) as exc_info:
            client.levels.modeled.get_area(TEST_AREA_ID)

        # Should raise SGUAPIError when JSON parsing fails
        assert "API request failed with status 500" in str(exc_info.value)
