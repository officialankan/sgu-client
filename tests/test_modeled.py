"""Tests for the modeled groundwater levels client, served canned responses by a fake transport.

They never touch the network. For canary tests that check the real SGU API still
works, see test_actual_api.py.
"""

from datetime import UTC, datetime

import pytest
from pandas.api.types import is_datetime64_any_dtype as is_datetime

from sgu_client import SGUClient
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
TEST_LEVEL_DATE = datetime(2024, 8, 1, tzinfo=UTC)
TEST_LEVEL_OBJECTID = 1


def test_create_basic_client() -> None:
    client = SGUClient()
    assert hasattr(client, "levels")
    assert hasattr(client.levels, "modeled")


def test_get_areas(fake, client) -> None:
    """Test getting modeled areas."""
    mock_response_data = create_mock_multiple_modeled_areas_response(
        area_ids=[30125, 30126], limit=10
    )
    fake.add("", mock_response_data)

    areas = client.levels.modeled.get_areas(limit=10)
    assert areas is not None
    assert isinstance(areas, ModeledAreaCollection)
    assert len(areas.features) > 0
    assert all(isinstance(area, ModeledArea) for area in areas.features)


def test_get_area_by_id(fake, client) -> None:
    """Test getting a specific area by ID."""
    mock_response_data = create_mock_single_modeled_area_response(
        area_id=TEST_AREA_ID, omrade_id=TEST_AREA_OMRADE_ID
    )
    fake.add("", mock_response_data)

    area = client.levels.modeled.get_area(TEST_AREA_ID)
    assert area is not None
    assert isinstance(area, ModeledArea)
    assert area.id == TEST_AREA_ID
    assert area.properties.area_id == TEST_AREA_OMRADE_ID
    assert area.geometry.type == "MultiPolygon"
    assert area.geometry.coordinates is not None


def test_get_area_not_found(fake, client) -> None:
    """Test handling of non-existent area requests."""
    mock_response_data = create_mock_empty_modeled_collection_response()
    fake.add("", mock_response_data)

    with pytest.raises(ValueError, match="Area .* not found"):
        client.levels.modeled.get_area("nonexistent.999999")


def test_get_levels(fake, client) -> None:
    """Test getting modeled levels."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

    levels = client.levels.modeled.get_levels(limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0
    assert all(isinstance(level, ModeledGroundwaterLevel) for level in levels.features)


def test_get_level_by_id(fake, client) -> None:
    """Test getting a specific level by ID."""
    mock_response_data = create_mock_single_modeled_level_response(
        level_id=TEST_LEVEL_ID,
        omrade_id=TEST_LEVEL_OMRADE_ID,
        datum=TEST_LEVEL_DATUM,
        objectid=TEST_LEVEL_OBJECTID,
    )
    fake.add("", mock_response_data)

    level = client.levels.modeled.get_level(TEST_LEVEL_ID)
    assert level is not None
    assert isinstance(level, ModeledGroundwaterLevel)
    assert level.id == TEST_LEVEL_ID
    assert level.properties.area_id == TEST_LEVEL_OMRADE_ID
    assert level.properties.date == TEST_LEVEL_DATE
    assert level.properties.object_id == TEST_LEVEL_OBJECTID


def test_get_level_not_found(fake, client) -> None:
    """Test handling of non-existent level requests."""
    mock_response_data = create_mock_empty_modeled_collection_response()
    fake.add("", mock_response_data)

    with pytest.raises(ValueError, match="Level .* not found"):
        client.levels.modeled.get_level("nonexistent.999999")


def test_areas_with_bbox(fake, client) -> None:
    """Test getting areas with bbox filter."""
    mock_response_data = create_mock_multiple_modeled_areas_response(
        area_ids=[30125, 30126], limit=5
    )
    fake.add("", mock_response_data)

    # Test with a bbox covering southern Sweden
    areas = client.levels.modeled.get_areas(bbox=[12.0, 55.0, 16.0, 58.0], limit=5)
    assert areas is not None
    assert isinstance(areas, ModeledAreaCollection)
    # Should have at least some areas in this region
    assert len(areas.features) >= 0


def test_levels_basic_query(fake, client) -> None:
    """Test basic levels query."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

    # Test basic query without datetime filtering (API seems to have issues with datetime)
    levels = client.levels.modeled.get_levels(limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # Check that we got some basic data structure
    for level in levels.features:
        assert level.properties.area_id is not None
        assert level.properties.object_id is not None


def test_levels_with_filter_expr(fake, client) -> None:
    """Test levels query with filter expression."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=3
    )
    fake.add("", mock_response_data)

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


def test_levels_with_sortby(fake, client) -> None:
    """Test levels query with sorting."""
    # Create levels with descending dates
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=3
    )
    # Reverse the order to simulate descending sort
    mock_response_data["features"].reverse()
    fake.add("", mock_response_data)

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


def test_areas_to_dataframe(fake, client) -> None:
    """Test converting areas to DataFrame."""
    mock_response_data = create_mock_multiple_modeled_areas_response(
        area_ids=[TEST_AREA_OMRADE_ID, 30126], limit=5
    )
    fake.add("", mock_response_data)

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


def test_levels_to_dataframe(fake, client) -> None:
    """Test converting levels to DataFrame."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

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


def test_levels_to_series(fake, client) -> None:
    """Test converting levels to Series."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

    levels = client.levels.modeled.get_levels(limit=5)
    assert levels is not None
    series = levels.to_series()
    assert not series.empty

    assert is_datetime(series.index)


def test_levels_to_series_custom_index_data(fake, client) -> None:
    """Test converting levels to Series with custom index/data columns."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

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


def test_levels_to_dataframe_no_sort(fake, client) -> None:
    """Test converting levels to DataFrame without sorting."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

    levels = client.levels.modeled.get_levels(limit=5)
    assert levels is not None
    df = levels.to_dataframe(sort_by_date=False)
    assert not df.empty
    assert "date" in df.columns


def test_date_property_parsing(fake, client) -> None:
    """Test date property parsing."""
    mock_response_data = create_mock_single_modeled_level_response(
        level_id=TEST_LEVEL_ID,
        omrade_id=TEST_LEVEL_OMRADE_ID,
        datum=TEST_LEVEL_DATUM,
        objectid=TEST_LEVEL_OBJECTID,
    )
    fake.add("", mock_response_data)

    level = client.levels.modeled.get_level(TEST_LEVEL_ID)
    assert level.properties.date == TEST_LEVEL_DATE


def test_percentile_validation(fake, client) -> None:
    """Test percentile value validation."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

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


def test_get_levels_by_area(fake, client) -> None:
    """Test getting levels by area ID."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

    levels = client.levels.modeled.get_levels_by_area(TEST_LEVEL_OMRADE_ID, limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # All results should have the specified area ID
    for level in levels.features:
        assert level.properties.area_id == TEST_LEVEL_OMRADE_ID


def test_get_levels_by_area_to_dataframe(fake, client) -> None:
    """Test converting levels by area to DataFrame."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

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


def test_get_levels_by_area_with_limit(fake, client) -> None:
    """Test getting levels by area with limit."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=3
    )
    fake.add("", mock_response_data)

    levels = client.levels.modeled.get_levels_by_area(TEST_LEVEL_OMRADE_ID, limit=5)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) <= 5

    # All results should have the specified area ID
    for level in levels.features:
        assert level.properties.area_id == TEST_LEVEL_OMRADE_ID


def test_get_levels_by_areas(fake, client) -> None:
    """Test getting levels by multiple area IDs."""
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
    fake.add("", mock_response_data)

    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=20)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) > 0

    # All results should have one of the specified area IDs
    for level in levels.features:
        assert level.properties.area_id in area_ids


def test_get_levels_by_areas_single_area(fake, client) -> None:
    """Test getting levels by single area ID in list."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

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


def test_get_levels_by_areas_to_dataframe(fake, client) -> None:
    """Test converting levels by multiple areas to DataFrame."""
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
    fake.add("", mock_response_data)

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


def test_get_levels_by_areas_with_limit(fake, client) -> None:
    """Test getting levels by multiple areas with limit."""
    area_ids = [TEST_LEVEL_OMRADE_ID, 30126]
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=3
    )
    fake.add("", mock_response_data)

    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=5)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)
    assert len(levels.features) <= 5

    # All results should have one of the specified area IDs
    for level in levels.features:
        assert level.properties.area_id in area_ids


def test_get_levels_by_areas_mixed_existing_nonexistent(fake, client) -> None:
    """Test mixed existing/non-existent area IDs."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("", mock_response_data)

    # Mix existing and non-existent area IDs
    area_ids = [TEST_LEVEL_OMRADE_ID, 999999]
    levels = client.levels.modeled.get_levels_by_areas(area_ids, limit=10)
    assert levels is not None
    assert isinstance(levels, ModeledGroundwaterLevelCollection)

    # Should only have levels from the existing area
    for level in levels.features:
        assert level.properties.area_id == TEST_LEVEL_OMRADE_ID


def test_get_levels_by_coords_single_area(fake, client) -> None:
    """Test get_levels_by_coords with coordinates that find a single area."""
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID, count=5
    )
    fake.add("omraden/items", create_mock_single_modeled_area_response())
    fake.add("grundvattennivaer-tidigare/items", mock_response_data)

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


def test_get_levels_by_coords_boundary_warning(fake, client, caplog) -> None:
    """Test get_levels_by_coords with coordinates near boundary (multiple areas)."""
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
    # area lookup returns two areas (boundary case), then the levels
    fake.add(
        "",
        create_mock_multiple_modeled_areas_response(area_ids=[30125, 30126]),
        mock_response_data,
    )

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


def test_get_levels_by_coords_outside_sweden(fake, client) -> None:
    """Test get_levels_by_coords with coordinates outside Sweden."""
    mock_response_data = create_mock_empty_modeled_collection_response()
    fake.add("", mock_response_data)

    # Test with coordinates outside Sweden (London)
    with pytest.raises(
        ValueError, match="No modeled groundwater areas found near coordinates"
    ):
        client.levels.modeled.get_levels_by_coords(lat=51.5074, lon=-0.1278, limit=5)


def test_get_levels_by_coords_with_datetime(fake, client) -> None:
    """Test get_levels_by_coords with datetime filtering."""
    from datetime import UTC, datetime

    # Create 2023 data
    mock_response_data = create_mock_multiple_modeled_levels_response(
        omrade_id=TEST_LEVEL_OMRADE_ID,
        count=3,
        start_date=datetime(2023, 1, 1, tzinfo=UTC),
    )
    fake.add("omraden/items", create_mock_single_modeled_area_response())
    fake.add("grundvattennivaer-tidigare/items", mock_response_data)

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


def test_get_levels_by_coords_searches_areas_within_the_buffer(fake, client) -> None:
    """The area lookup covers ``buffer`` degrees around the point."""
    fake.add("omraden/items", create_mock_single_modeled_area_response())
    fake.add(
        "grundvattennivaer-tidigare/items",
        create_mock_empty_modeled_collection_response(),
    )

    client.levels.modeled.get_levels_by_coords(lat=57.5, lon=12.0, buffer=0.25)

    area_lookup = fake.requests[0]
    assert area_lookup.url.endswith("collections/omraden/items")
    assert area_lookup.params["bbox"] == "11.75,57.25,12.25,57.75"


# Responses with no feature, or several where one was expected
def test_empty_area_response_handling(fake, client) -> None:
    """Test handling of empty area responses."""
    mock_response_data = create_mock_empty_modeled_collection_response()
    fake.add("", mock_response_data)

    with pytest.raises(ValueError, match="Area .* not found"):
        client.levels.modeled.get_area("nonexistent.area")


def test_empty_level_response_handling(fake, client) -> None:
    """Test handling of empty level responses."""
    mock_response_data = create_mock_empty_modeled_collection_response()
    fake.add("", mock_response_data)

    with pytest.raises(ValueError, match="Level .* not found"):
        client.levels.modeled.get_level("nonexistent.level")


@pytest.mark.parametrize(
    ("area_ids", "expected"),
    [
        (["30125"], "omrade_id=30125"),
        ([30125, "30126"], "omrade_id in (30125, 30126)"),
    ],
)
def test_get_levels_by_areas_sends_area_ids_unquoted(
    client, fake, area_ids, expected
) -> None:
    """Area IDs are numbers in the API, even when passed as strings."""
    fake.add("", create_mock_empty_modeled_collection_response())
    client.levels.modeled.get_levels_by_areas(area_ids)

    assert fake.params["filter"] == expected


DATUM_JAN_2024 = (
    "datum >= '2024-01-01T00:00:00+00:00' AND datum <= '2024-01-31T00:00:00+00:00'"
)


@pytest.mark.parametrize(
    ("call", "expected_area_filter"),
    [
        (
            lambda modeled, **t: modeled.get_levels_by_area(30125, **t),
            "omrade_id=30125",
        ),
        (
            lambda modeled, **t: modeled.get_levels_by_areas([30125, 30126], **t),
            "omrade_id in (30125, 30126)",
        ),
    ],
)
def test_get_levels_by_area_filters_on_date(
    client, fake, call, expected_area_filter
) -> None:
    """tmin/tmax filter modeled levels on their date, like observed measurements."""
    fake.add("", create_mock_empty_modeled_collection_response())
    call(
        client.levels.modeled,
        tmin=datetime(2024, 1, 1, tzinfo=UTC),
        tmax=datetime(2024, 1, 31, tzinfo=UTC),
    )

    assert fake.params["filter"] == (f"{expected_area_filter} AND {DATUM_JAN_2024}")


def test_get_levels_by_coords_filters_on_date(fake, client) -> None:
    """tmin/tmax reach the levels request, not the area lookup."""
    area = create_mock_single_modeled_area_response()
    area_id = area["features"][0]["properties"]["omrade_id"]
    fake.add("", area, create_mock_empty_modeled_collection_response())
    client.levels.modeled.get_levels_by_coords(
        lat=57.7, lon=11.97, tmin="2024-01-01", tmax="2024-01-31"
    )

    area_params, level_params = (call.params for call in fake.requests)
    assert "filter" not in area_params
    assert level_params["filter"] == (
        f"omrade_id={area_id} AND datum >= '2024-01-01' AND datum <= '2024-01-31'"
    )


def test_get_levels_filters_on_date(fake, client) -> None:
    fake.add("", create_mock_empty_modeled_collection_response())
    client.levels.modeled.get_levels(tmin="2024-01-01", tmax="2024-01-31")

    assert fake.params["filter"] == ("datum >= '2024-01-01' AND datum <= '2024-01-31'")
