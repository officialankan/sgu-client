"""Dates from the SGU API become tz-aware datetimes, exactly as the wire states.

Every value the API sends ends in ``Z`` (UTC). Date-only values such as
``"1996-04-29Z"`` become midnight UTC. Null stays ``None``; anything unparseable,
including a value without any timezone, becomes ``None`` and logs a warning.
"""

from datetime import UTC, datetime

import pytest

from sgu_client.models.chemistry import (
    AnalysisResultCollection,
    AnalysisResultProperties,
    SamplingSiteCollection,
    SamplingSiteProperties,
)
from sgu_client.models.modeled import (
    ModeledAreaCollection,
    ModeledGroundwaterLevelCollection,
    ModeledGroundwaterLevelProperties,
)
from sgu_client.models.observed import (
    GroundwaterMeasurementCollection,
    GroundwaterMeasurementProperties,
    GroundwaterStationCollection,
    GroundwaterStationProperties,
)


def test_station_dates_parse_date_only_values_as_midnight_utc():
    props = GroundwaterStationProperties(
        **{"rowid": 1, "fdat": "1996-04-29Z", "tdat": "2018-12-10Z"}
    )

    assert props.active_since == datetime(1996, 4, 29, tzinfo=UTC)
    assert props.active_until == datetime(2018, 12, 10, tzinfo=UTC)


def test_null_active_until_means_live_station():
    props = GroundwaterStationProperties(**{"rowid": 1, "tdat": None})

    assert props.active_until is None


def test_unparseable_value_becomes_none_and_warns(caplog):
    props = GroundwaterStationProperties(**{"rowid": 1, "tdat": "not-a-date"})

    assert props.active_until is None
    assert "active_until" in caplog.text
    assert "not-a-date" in caplog.text


def test_value_without_timezone_becomes_none_and_warns(caplog):
    props = GroundwaterStationProperties(**{"rowid": 1, "fdat": "1996-04-29"})

    assert props.active_since is None
    assert "'1996-04-29'" in caplog.text


def test_dumped_model_validates_back_to_the_same_datetimes():
    props = GroundwaterStationProperties(**{"rowid": 1, "fdat": "1996-04-29Z"})

    again = GroundwaterStationProperties(**props.model_dump())

    assert again.active_since == datetime(1996, 4, 29, tzinfo=UTC)


def test_measurement_timestamps_parse_as_utc():
    props = GroundwaterMeasurementProperties(
        **{
            "rowid": 1,
            "obsdatum": "2024-12-31T04:00:00Z",
            "lastupdate": "2025-01-01T06:10:09.790Z",
        }
    )

    assert props.observation_date == datetime(2024, 12, 31, 4, tzinfo=UTC)
    assert props.last_updated == datetime(2025, 1, 1, 6, 10, 9, 790000, tzinfo=UTC)


def test_modeled_date_parses_as_midnight_utc():
    props = ModeledGroundwaterLevelProperties(
        **{"datum": "1968-11-25Z", "omrade_id": 1, "objectid": 1}
    )

    assert props.date == datetime(1968, 11, 25, tzinfo=UTC)


def test_sampling_site_dates_parse_as_midnight_utc():
    props = SamplingSiteProperties(
        **{
            "etabldatum": "2022-09-07Z",
            "forstaprov": "2022-09-08Z",
            "senasteprov": "2022-09-09Z",
        }
    )

    assert props.established_date == datetime(2022, 9, 7, tzinfo=UTC)
    assert props.first_sample_date == datetime(2022, 9, 8, tzinfo=UTC)
    assert props.latest_sample_date == datetime(2022, 9, 9, tzinfo=UTC)


def test_analysis_result_dates_parse_as_utc():
    props = AnalysisResultProperties(
        **{
            "provtagningsdatum": "2013-08-27T00:00:00Z",
            "provtagning_slutdatum": "2013-08-28T00:00:00Z",
            "registreringsdatum": "2013-09-01T00:00:00Z",
            "analysdatum": None,
        }
    )

    assert props.sampling_date == datetime(2013, 8, 27, tzinfo=UTC)
    assert props.sampling_end_date == datetime(2013, 8, 28, tzinfo=UTC)
    assert props.registration_date == datetime(2013, 9, 1, tzinfo=UTC)
    assert props.analysis_date is None


@pytest.mark.parametrize(
    "collection_cls",
    [
        GroundwaterStationCollection,
        GroundwaterMeasurementCollection,
        ModeledAreaCollection,
        ModeledGroundwaterLevelCollection,
        SamplingSiteCollection,
        AnalysisResultCollection,
    ],
)
def test_collection_timestamp_parses_as_utc(collection_cls):
    collection = collection_cls(
        **{
            "type": "FeatureCollection",
            "features": [],
            "timeStamp": "2026-10-19T18:31:20.436Z",
        }
    )

    assert collection.timeStamp == datetime(
        2026, 10, 19, 18, 31, 20, 436000, tzinfo=UTC
    )


# DataFrames: date columns are always UTC datetimes, even when every value is null


def _assert_utc_datetime_column(df, column):
    pd = pytest.importorskip("pandas")
    assert isinstance(df[column].dtype, pd.DatetimeTZDtype), column
    assert str(df[column].dtype.tz) == "UTC", column
    assert df[column].dtype.unit == "ns", column


def _feature(feature_id, properties):
    return {
        "type": "Feature",
        "id": feature_id,
        "geometry": None,
        "properties": properties,
    }


def test_stations_dataframe_has_utc_date_columns_with_nat_for_live_stations():
    pd = pytest.importorskip("pandas")
    stations = GroundwaterStationCollection(
        features=[
            _feature("stationer.1", {"rowid": 1, "fdat": "1996-04-29Z", "tdat": None}),
            _feature("stationer.2", {"rowid": 2, "fdat": None, "tdat": None}),
        ]
    )

    df = stations.to_dataframe()

    _assert_utc_datetime_column(df, "active_since")
    _assert_utc_datetime_column(df, "active_until")
    assert df["active_since"].iloc[0] == pd.Timestamp("1996-04-29", tz="UTC")
    assert df["active_until"].isna().all()


def test_measurements_dataframe_has_utc_timestamps_and_no_duplicate_last_update():
    pd = pytest.importorskip("pandas")
    measurements = GroundwaterMeasurementCollection(
        features=[
            _feature(
                "nivaer.1",
                {"rowid": 1, "obsdatum": "2024-12-31T04:00:00Z", "lastupdate": None},
            )
        ]
    )

    df = measurements.to_dataframe()

    _assert_utc_datetime_column(df, "observation_date")
    _assert_utc_datetime_column(df, "last_updated")
    assert df["observation_date"].iloc[0] == pd.Timestamp("2024-12-31 04:00", tz="UTC")
    assert "last_update" not in df.columns


def _modeled_levels(*datums):
    return ModeledGroundwaterLevelCollection(
        features=[
            _feature(
                f"grundvattennivaer-tidigare.{i}",
                {"datum": datum, "omrade_id": 1, "objectid": i, "fyllnadsgrad_sma": i},
            )
            for i, datum in enumerate(datums)
        ]
    )


def test_modeled_levels_dataframe_has_utc_date_column_even_when_all_null():
    df = _modeled_levels(None).to_dataframe()

    _assert_utc_datetime_column(df, "date")


def test_modeled_levels_series_index_is_utc():
    pd = pytest.importorskip("pandas")

    series = _modeled_levels("1968-11-25Z").to_series()

    assert series.index[0] == pd.Timestamp("1968-11-25", tz="UTC")


def test_chemistry_dataframes_have_utc_date_columns_even_when_all_null():
    sites = SamplingSiteCollection(
        features=[_feature("provplatser.1", {"etabldatum": "2022-09-07Z"})]
    )
    results = AnalysisResultCollection(
        features=[
            _feature("analysresultat.1", {"provtagningsdatum": "2013-08-27T00:00:00Z"})
        ]
    )

    sites_df = sites.to_dataframe()
    results_df = results.to_dataframe()

    for column in ("established_date", "first_sample_date", "latest_sample_date"):
        _assert_utc_datetime_column(sites_df, column)
    for column in (
        "sampling_date",
        "sampling_end_date",
        "registration_date",
        "analysis_date",
    ):
        _assert_utc_datetime_column(results_df, column)
