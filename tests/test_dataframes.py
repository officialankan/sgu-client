"""How every collection converts to a pandas DataFrame or Series."""

from datetime import UTC, datetime
from typing import Any, NamedTuple

import pytest
from pydantic import BaseModel

from sgu_client.models.chemistry import (
    AnalysisResultCollection,
    AnalysisResultProperties,
    SamplingSiteCollection,
    SamplingSiteProperties,
)
from sgu_client.models.features import FeatureCollection
from sgu_client.models.modeled import (
    ModeledAreaCollection,
    ModeledAreaProperties,
    ModeledGroundwaterLevelCollection,
    ModeledGroundwaterLevelProperties,
)
from sgu_client.models.observed import (
    GroundwaterMeasurementCollection,
    GroundwaterMeasurementProperties,
    GroundwaterStationCollection,
    GroundwaterStationProperties,
)
from tests.mock_responses import (
    create_mock_analysis_result_collection_response,
    create_mock_analysis_result_feature,
    create_mock_measurement_collection_response,
    create_mock_modeled_area_collection_response,
    create_mock_modeled_area_feature,
    create_mock_modeled_level_collection_response,
    create_mock_sampling_site_collection_response,
    create_mock_single_station_response,
)

pytest.importorskip("pandas")


class Case(NamedTuple):
    collection: type[FeatureCollection[Any]]
    properties: type[BaseModel]
    response: dict[str, Any]  # with one feature
    feature_id: str  # of that feature
    leading: list[str]  # columns before the properties


CASES = [
    Case(
        GroundwaterStationCollection,
        GroundwaterStationProperties,
        create_mock_single_station_response(),
        "stationer.4086",
        ["feature_id", "longitude", "latitude"],
    ),
    Case(
        GroundwaterMeasurementCollection,
        GroundwaterMeasurementProperties,
        create_mock_measurement_collection_response(),
        "nivaer.1",
        ["feature_id"],
    ),
    Case(
        ModeledAreaCollection,
        ModeledAreaProperties,
        create_mock_modeled_area_collection_response(),
        "omraden.30125",
        ["feature_id", "centroid_longitude", "centroid_latitude"],
    ),
    Case(
        ModeledGroundwaterLevelCollection,
        ModeledGroundwaterLevelProperties,
        create_mock_modeled_level_collection_response(),
        "grundvattennivaer-tidigare.1",
        ["feature_id"],
    ),
    Case(
        SamplingSiteCollection,
        SamplingSiteProperties,
        create_mock_sampling_site_collection_response(),
        "provplatser.1560",
        ["feature_id", "longitude", "latitude"],
    ),
    Case(
        AnalysisResultCollection,
        AnalysisResultProperties,
        create_mock_analysis_result_collection_response(),
        "analysresultat.1757",
        ["feature_id"],
    ),
]

each_collection = pytest.mark.parametrize(
    "case", CASES, ids=[case.collection.__name__ for case in CASES]
)


@each_collection
def test_columns_are_feature_id_geometry_then_properties(case: Case):
    """Geometry columns depend on the collection, never on the data."""
    df = case.collection.model_validate(case.response).to_dataframe()

    n, fields = len(case.leading), list(case.properties.model_fields)
    assert list(df.columns[:n]) == case.leading
    assert list(df.columns[n : n + len(fields)]) == fields
    assert df["feature_id"].tolist() == [case.feature_id]


@each_collection
def test_empty_collections_keep_their_columns(case: Case):
    """Code like df["observation_date"] works without special-casing no results."""
    df = case.collection.model_validate(
        {**case.response, "features": []}
    ).to_dataframe()

    assert df.empty
    assert list(df.columns) == case.leading + list(case.properties.model_fields)


@each_collection
def test_unknown_total_features_is_none(case: Case):
    """SGU sometimes sends totalFeatures: "unknown"; every collection accepts it."""
    parsed = case.collection.model_validate(
        {**case.response, "totalFeatures": "unknown"}
    )

    assert parsed.totalFeatures is None


def test_empty_measurements_have_utc_date_column():
    """Empty date columns still have the UTC datetime dtype."""
    df = GroundwaterMeasurementCollection().to_dataframe()

    assert str(df["observation_date"].dtype) == "datetime64[ns, UTC]"


def test_geometry_values():
    """Points give their coordinates; areas the centre of their grid cell."""
    stations = GroundwaterStationCollection(**create_mock_single_station_response())
    # the mock area is the cell 11.8-12.2 E, 57.6-57.8 N
    areas = ModeledAreaCollection(**create_mock_modeled_area_collection_response())

    station = stations.to_dataframe().iloc[0]
    area = areas.to_dataframe().iloc[0]

    assert (station["longitude"], station["latitude"]) == (16.123456, 58.789012)
    assert area["centroid_longitude"] == pytest.approx(12.0)
    assert area["centroid_latitude"] == pytest.approx(57.7)


def test_area_centre_does_not_depend_on_the_first_corner():
    """GeoJSON repeats the first corner to close the ring; it must not count twice."""
    corners = [[11.8, 57.6], [12.2, 57.6], [12.2, 57.8], [11.8, 57.8]]
    rings = [corners[i:] + corners[:i] for i in range(4)]
    areas = ModeledAreaCollection(
        **create_mock_modeled_area_collection_response(
            [
                create_mock_modeled_area_feature(coordinates=[[[*ring, ring[0]]]])
                for ring in rings
            ]
        )
    )

    df = areas.to_dataframe()

    assert df["centroid_longitude"].tolist() == pytest.approx([12.0] * 4)
    assert df["centroid_latitude"].tolist() == pytest.approx([57.7] * 4)


def _results(*features: tuple[str, int, str]) -> AnalysisResultCollection:
    return AnalysisResultCollection(
        **create_mock_analysis_result_collection_response(
            [
                create_mock_analysis_result_feature(
                    result_id=result_id,
                    sampling_date=datetime(2021, month, 1, tzinfo=UTC),
                    parameternamn=parameter,
                )
                for result_id, month, parameter in features
            ]
        )
    )


def test_sorting_keeps_api_position_as_index():
    """The index is the row's position in the API response, sorted or not."""
    results = _results(("a", 3, "pH"), ("b", 1, "pH"), ("c", 2, "pH"))

    by_date = results.to_dataframe()
    api_order = results.to_dataframe(sort_by_date=False)

    assert by_date["feature_id"].tolist() == ["b", "c", "a"]
    assert by_date.index.tolist() == [1, 2, 0]
    assert api_order["feature_id"].tolist() == ["a", "b", "c"]
    assert api_order.index.tolist() == [0, 1, 2]


def test_rows_with_the_same_date_stay_in_api_order():
    """Several parameters from one sample share a date and keep their order."""
    parameters = ["pH", "Klorid", "Nitratkväve", "Sulfat", "Kalcium", "Järn"]
    results = _results(
        ("late", 2, "pH"),
        *((f"early-{p}", 1, p) for p in parameters * 4),
    )

    df = results.to_dataframe()

    assert df["parameter_name"].tolist()[:-1] == parameters * 4
    assert df["feature_id"].iloc[-1] == "late"


@pytest.mark.parametrize(
    "collection",
    [GroundwaterStationCollection, ModeledAreaCollection, SamplingSiteCollection],
)
def test_collections_without_dates_have_no_series(collection):
    """Only time series collections sort by date and convert to a Series."""
    assert not hasattr(collection, "to_series")


def test_stations_keep_feature_id_and_station_id():
    """The feature id no longer gets overwritten by the station id (#58)."""
    stations = GroundwaterStationCollection(**create_mock_single_station_response())

    df = stations.to_dataframe()

    assert df["feature_id"].iloc[0] == "stationer.4086"
    assert df["station_id"].iloc[0] == "95_2"
