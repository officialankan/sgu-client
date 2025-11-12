"""Tests for chemistry module with mocked API responses."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from requests import Response

from sgu_client import SGUClient
from sgu_client.exceptions import SGUAPIError, SGUConnectionError, SGUTimeoutError
from sgu_client.models.chemistry import (
    AnalysisResult,
    AnalysisResultCollection,
    SamplingSite,
    SamplingSiteCollection,
)
from tests.mock_responses import (
    create_mock_empty_chemistry_collection_response,
    create_mock_multiple_analysis_results_response,
    create_mock_single_sampling_site_response,
)


def create_mock_response(response_data, status_code=200):
    """Create a mock HTTP response object."""
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = status_code
    mock_response.json.return_value = response_data
    return mock_response


def test_chemistry_client_exists():
    """Test that chemistry client is accessible."""
    client = SGUClient()
    assert hasattr(client, "chemistry")
    assert hasattr(client.chemistry, "get_sampling_sites")
    assert hasattr(client.chemistry, "get_analysis_results")


def test_chemistry_models_importable():
    """Test that chemistry models can be imported."""
    assert AnalysisResult is not None
    assert AnalysisResultCollection is not None
    assert SamplingSite is not None
    assert SamplingSiteCollection is not None


def test_get_sampling_sites_with_mock():
    """Test getting sampling sites with mocked response."""
    client = SGUClient()

    # Create mock response for a single sampling site
    mock_response_data = create_mock_single_sampling_site_response(
        site_id="provplatser.3",
        platsbeteckning="10001_1",
        provplatsnamn="Test_Site",
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the method
        sites = client.chemistry.get_sampling_sites(limit=1)

        # Verify results
        assert sites is not None
        assert isinstance(sites, SamplingSiteCollection)
        assert len(sites.features) == 1
        assert sites.features[0].properties.station_id == "10001_1"
        assert sites.features[0].properties.site_name == "Test_Site"


def test_get_analysis_results_with_mock():
    """Test getting analysis results with mocked response."""
    client = SGUClient()

    # Create mock response for analysis results
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[("pH", "PH", 7.2)],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the method
        results = client.chemistry.get_analysis_results(limit=1)

        # Verify results
        assert results is not None
        assert isinstance(results, AnalysisResultCollection)
        assert len(results.features) == 1
        assert results.features[0].properties.station_id == "10001_1"
        assert results.features[0].properties.parameter_short_name == "PH"
        assert results.features[0].properties.measurement_value == 7.2


def test_get_sampling_site_by_name_station_id():
    """Test getting a single sampling site by station_id with mocked response."""
    client = SGUClient()

    # Create mock response with one site matching the station_id
    mock_response_data = create_mock_single_sampling_site_response(
        site_id="provplatser.3",
        platsbeteckning="10001_1",
        provplatsnamn="Test_Site",
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the convenience method
        site = client.chemistry.get_sampling_site_by_name(station_id="10001_1")

        # Verify results
        assert site is not None
        assert isinstance(site, SamplingSite)
        assert site.properties.station_id == "10001_1"
        assert site.properties.site_name == "Test_Site"


def test_get_sampling_site_by_name_site_name():
    """Test getting a single sampling site by site_name with mocked response."""
    client = SGUClient()

    # Create mock response with one site matching the site_name
    mock_response_data = create_mock_single_sampling_site_response(
        site_id="provplatser.3",
        platsbeteckning="10001_1",
        provplatsnamn="Test_Site",
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the convenience method using site_name
        site = client.chemistry.get_sampling_site_by_name(site_name="Test_Site")

        # Verify results
        assert site is not None
        assert isinstance(site, SamplingSite)
        assert site.properties.station_id == "10001_1"
        assert site.properties.site_name == "Test_Site"


def test_get_sampling_sites_by_names():
    """Test getting multiple sampling sites by names with mocked response."""
    from tests.mock_responses import create_mock_multiple_sampling_sites_response

    client = SGUClient()

    # Create mock response with multiple sites
    mock_response_data = create_mock_multiple_sampling_sites_response(
        platsbeteckningar=["10001_1", "10002_1"],
        limit=10,
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the convenience method for multiple sites
        sites = client.chemistry.get_sampling_sites_by_names(
            station_id=["10001_1", "10002_1"]
        )

        # Verify results
        assert sites is not None
        assert isinstance(sites, SamplingSiteCollection)
        assert len(sites.features) == 2
        assert sites.features[0].properties.station_id == "10001_1"
        assert sites.features[1].properties.station_id == "10002_1"


def test_get_results_by_site_with_station_id():
    """Test getting analysis results for a specific site by station_id."""
    client = SGUClient()

    # Create mock response with analysis results for one site
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[
            ("pH", "PH", 7.2),
            ("Nitrat", "NITRATE", 12.5),
        ],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the convenience method
        results = client.chemistry.get_results_by_site(station_id="10001_1", limit=10)

        # Verify results
        assert results is not None
        assert isinstance(results, AnalysisResultCollection)
        assert len(results.features) == 2
        # All results should be from the same station
        assert all(r.properties.station_id == "10001_1" for r in results.features)
        # Verify we got both parameters
        params = [r.properties.parameter_short_name for r in results.features]
        assert "PH" in params
        assert "NITRATE" in params


def test_get_results_by_site_with_time_filtering():
    """Test getting analysis results for a site with time filtering."""
    from datetime import UTC, datetime

    client = SGUClient()

    # Create mock response
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[("pH", "PH", 7.2)],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call with time filtering
        results = client.chemistry.get_results_by_site(
            station_id="10001_1",
            tmin=datetime(2020, 1, 1, tzinfo=UTC),
            tmax=datetime(2021, 1, 1, tzinfo=UTC),
            limit=10,
        )

        # Verify results
        assert results is not None
        assert isinstance(results, AnalysisResultCollection)
        assert len(results.features) > 0


def test_get_results_by_sites():
    """Test getting analysis results for multiple sites."""
    client = SGUClient()

    # Create mock response with results from multiple sites
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[
            ("pH", "PH", 7.2),
            ("pH", "PH", 7.4),
        ],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        # Call the convenience method for multiple sites
        results = client.chemistry.get_results_by_sites(
            station_id=["10001_1", "10002_1"], limit=10
        )

        # Verify results
        assert results is not None
        assert isinstance(results, AnalysisResultCollection)
        assert len(results.features) == 2
        # Verify all results have a station_id
        assert all(r.properties.station_id is not None for r in results.features)


def test_sampling_sites_to_dataframe():
    """Test converting sampling sites collection to pandas DataFrame."""
    from tests.mock_responses import create_mock_multiple_sampling_sites_response

    client = SGUClient()

    # Create mock response with multiple sites
    mock_response_data = create_mock_multiple_sampling_sites_response(
        platsbeteckningar=["10001_1", "10002_1"],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        sites = client.chemistry.get_sampling_sites(limit=10)
        df = sites.to_dataframe()

        # Verify DataFrame structure
        assert df is not None
        assert not df.empty
        assert len(df) == 2

        # Verify key columns exist
        assert "site_id" in df.columns
        assert "station_id" in df.columns
        assert "site_name" in df.columns
        assert "municipality" in df.columns
        assert "sample_count" in df.columns

        # Verify data
        assert "10001_1" in df["station_id"].values
        assert "10002_1" in df["station_id"].values


def test_analysis_results_to_dataframe():
    """Test converting analysis results collection to pandas DataFrame."""
    from pandas.api.types import is_datetime64_any_dtype as is_datetime

    client = SGUClient()

    # Create mock response with multiple parameters
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[
            ("pH", "PH", 7.2),
            ("Nitrat", "NITRATE", 12.5),
            ("Klorid", "KLORID", 8.3),
        ],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        results = client.chemistry.get_analysis_results(limit=10)
        df = results.to_dataframe()

        # Verify DataFrame structure
        assert df is not None
        assert not df.empty
        assert len(df) == 3

        # Verify key columns exist
        assert "result_id" in df.columns
        assert "sampling_date" in df.columns
        assert "parameter_short_name" in df.columns
        assert "measurement_value" in df.columns
        assert "unit" in df.columns

        # Verify datetime column is properly typed
        assert is_datetime(df["sampling_date"])

        # Verify data
        assert "PH" in df["parameter_short_name"].values
        assert "NITRATE" in df["parameter_short_name"].values
        assert "KLORID" in df["parameter_short_name"].values


def test_analysis_results_to_series():
    """Test converting analysis results to pandas Series."""
    client = SGUClient()

    # Create mock response with single parameter measurements
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[
            ("pH", "PH", 7.2),
            ("pH", "PH", 7.4),
            ("pH", "PH", 7.1),
        ],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        results = client.chemistry.get_analysis_results(limit=10)
        series = results.to_series()

        # Verify Series structure
        assert series is not None
        assert not series.empty
        assert len(series) == 3
        assert series.name == "measurement_value"

        # Verify values
        assert 7.2 in series.values
        assert 7.4 in series.values
        assert 7.1 in series.values


def test_analysis_results_pivot_by_parameter():
    """Test pivoting analysis results by parameter for multi-parameter analysis."""
    client = SGUClient()

    # Create mock response with multiple parameters over time
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[
            ("pH", "PH", 7.2),
            ("Nitrat", "NITRATE", 12.5),
            ("Klorid", "KLORID", 8.3),
        ],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        results = client.chemistry.get_analysis_results(limit=10)
        df_pivot = results.pivot_by_parameter()

        # Verify pivoted DataFrame structure
        assert df_pivot is not None
        assert not df_pivot.empty

        # Verify columns are parameter names
        assert "PH" in df_pivot.columns
        assert "NITRATE" in df_pivot.columns
        assert "KLORID" in df_pivot.columns

        # Verify we can access values by parameter
        assert df_pivot["PH"].notna().any()
        assert df_pivot["NITRATE"].notna().any()
        assert df_pivot["KLORID"].notna().any()


# Parameter validation tests
def test_get_sampling_site_by_name_no_args():
    """Test that get_sampling_site_by_name raises error when no arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError, match="Either 'station_id' or 'site_name' must be provided."
    ):
        client.chemistry.get_sampling_site_by_name()


def test_get_sampling_site_by_name_both_args():
    """Test that get_sampling_site_by_name raises error when both arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'station_id' or 'site_name' can be provided.",
    ):
        client.chemistry.get_sampling_site_by_name(
            station_id="10001_1", site_name="Test_Site"
        )


def test_get_sampling_sites_by_names_no_args():
    """Test that get_sampling_sites_by_names raises error when no arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Either 'station_id' or 'site_name' must be provided.",
    ):
        client.chemistry.get_sampling_sites_by_names()


def test_get_sampling_sites_by_names_both_args():
    """Test that get_sampling_sites_by_names raises error when both arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'station_id' or 'site_name' can be provided.",
    ):
        client.chemistry.get_sampling_sites_by_names(
            station_id=["10001_1"], site_name=["Test_Site"]
        )


def test_get_sampling_sites_by_names_empty_list():
    """Test that get_sampling_sites_by_names raises error when empty list provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Either 'station_id' or 'site_name' must be provided.",
    ):
        client.chemistry.get_sampling_sites_by_names(station_id=[])


def test_get_results_by_site_no_args():
    """Test that get_results_by_site raises error when no arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError, match="Either 'station_id' or 'site_name' must be provided."
    ):
        client.chemistry.get_results_by_site()


def test_get_results_by_site_both_args():
    """Test that get_results_by_site raises error when both arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'station_id' or 'site_name' can be provided.",
    ):
        client.chemistry.get_results_by_site(
            station_id="10001_1", site_name="Test_Site"
        )


def test_get_results_by_sites_no_args():
    """Test that get_results_by_sites raises error when no arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError, match="Either 'station_id' or 'site_name' must be provided."
    ):
        client.chemistry.get_results_by_sites()


def test_get_results_by_sites_both_args():
    """Test that get_results_by_sites raises error when both arguments provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Only one of 'station_id' or 'station_name' can be provided.",
    ):
        client.chemistry.get_results_by_sites(
            station_id=["10001_1"], site_name=["Test_Site"]
        )


def test_get_results_by_sites_empty_list():
    """Test that get_results_by_sites raises error when empty list provided."""
    client = SGUClient()
    with pytest.raises(
        ValueError,
        match="Either 'station_id' or 'site_name' must be provided.",
    ):
        client.chemistry.get_results_by_sites(station_id=[])


def test_get_results_by_parameter_no_parameter():
    """Test that get_results_by_parameter raises error when parameter not provided."""
    client = SGUClient()
    with pytest.raises(TypeError):
        client.chemistry.get_results_by_parameter()


# Error condition tests
def test_api_timeout_error():
    """Test that API timeout errors are properly raised."""
    import requests.exceptions

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = requests.exceptions.ReadTimeout("Read timeout")

        client = SGUClient()
        with pytest.raises(SGUTimeoutError, match="Read timeout"):
            client.chemistry.get_sampling_sites()


def test_api_connection_error():
    """Test that API connection errors are properly raised."""
    import requests.exceptions

    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        client = SGUClient()
        with pytest.raises(SGUConnectionError, match="Connection failed"):
            client.chemistry.get_sampling_sites()


def test_api_server_error():
    """Test that API server errors are properly raised."""
    with patch("requests.Session.request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal Server Error"}
        mock_request.return_value = mock_response

        client = SGUClient()
        with pytest.raises(SGUAPIError, match="API request failed with status 500"):
            client.chemistry.get_sampling_sites()


def test_api_not_found_error():
    """Test that API 404 errors are properly raised."""
    with patch("requests.Session.request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Site not found"}
        mock_request.return_value = mock_response

        client = SGUClient()
        with pytest.raises(SGUAPIError, match="API request failed with status 404"):
            client.chemistry.get_sampling_site("nonexistent.site")


def test_malformed_json_response():
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
            client.chemistry.get_sampling_sites()

        # Should raise SGUAPIError when JSON parsing fails
        assert "API request failed with status 500" in str(exc_info.value)


# Edge case tests
def test_empty_sampling_site_response_handling():
    """Test handling of empty sampling site responses."""
    with patch("requests.Session.request") as mock_request:
        mock_response_data = create_mock_empty_chemistry_collection_response()
        mock_request.return_value = create_mock_response(mock_response_data)

        client = SGUClient()
        with pytest.raises(ValueError, match="Site .* not found"):
            client.chemistry.get_sampling_site("nonexistent.site")


def test_empty_analysis_result_response_handling():
    """Test handling of empty analysis result responses."""
    with patch("requests.Session.request") as mock_request:
        mock_response_data = create_mock_empty_chemistry_collection_response()
        mock_request.return_value = create_mock_response(mock_response_data)

        client = SGUClient()
        with pytest.raises(ValueError, match="Result .* not found"):
            client.chemistry.get_analysis_result("nonexistent.result")


def test_multiple_sampling_sites_response_handling():
    """Test handling of multiple sites returned for single ID (edge case)."""
    from tests.mock_responses import create_mock_multiple_sampling_sites_response

    with patch("requests.Session.request") as mock_request:
        # Create response with multiple sites (should not happen but test edge case)
        mock_response_data = create_mock_multiple_sampling_sites_response(
            platsbeteckningar=["duplicate_1", "duplicate_2"],
        )
        mock_request.return_value = create_mock_response(mock_response_data)

        client = SGUClient()
        with pytest.raises(ValueError, match="Multiple sites returned for ID"):
            client.chemistry.get_sampling_site("duplicate.site")


def test_multiple_analysis_results_response_handling():
    """Test handling of multiple results returned for single ID (edge case)."""
    with patch("requests.Session.request") as mock_request:
        # Create response with multiple results
        mock_response_data = create_mock_multiple_analysis_results_response(
            platsbeteckning="10001_1",
            parameters=[("pH", "PH", 7.2), ("pH", "PH", 7.4)],
        )
        mock_request.return_value = create_mock_response(mock_response_data)

        client = SGUClient()
        with pytest.raises(ValueError, match="Multiple results returned for ID"):
            client.chemistry.get_analysis_result("duplicate.result")


# Internal helper method tests
def test_build_datetime_filters_helper():
    """Test the internal datetime filter building helper function."""
    client = SGUClient()

    # Test both tmin and tmax
    tmin = datetime(2020, 1, 1, tzinfo=UTC)
    tmax = datetime(2021, 1, 1, tzinfo=UTC)
    filters = client.chemistry._build_datetime_filters(tmin, tmax)
    expected = [
        "provtagningsdat >= '2020-01-01T00:00:00+00:00'",
        "provtagningsdat <= '2021-01-01T00:00:00+00:00'",
    ]
    assert filters == expected

    # Test only tmin
    filters = client.chemistry._build_datetime_filters(tmin, None)
    expected = ["provtagningsdat >= '2020-01-01T00:00:00+00:00'"]
    assert filters == expected

    # Test only tmax
    filters = client.chemistry._build_datetime_filters(None, tmax)
    expected = ["provtagningsdat <= '2021-01-01T00:00:00+00:00'"]
    assert filters == expected

    # Test string inputs
    filters = client.chemistry._build_datetime_filters(
        "2020-01-01T00:00:00Z", "2021-01-01T00:00:00Z"
    )
    expected = [
        "provtagningsdat >= '2020-01-01T00:00:00Z'",
        "provtagningsdat <= '2021-01-01T00:00:00Z'",
    ]
    assert filters == expected

    # Test no inputs
    filters = client.chemistry._build_datetime_filters(None, None)
    assert filters == []


# Advanced pandas tests
def test_analysis_results_to_series_custom_index_data():
    """Test converting analysis results to Series with custom index/data columns."""
    client = SGUClient()

    # Create mock response
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[
            ("pH", "PH", 7.2),
            ("pH", "PH", 7.4),
            ("pH", "PH", 7.1),
        ],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        results = client.chemistry.get_analysis_results(limit=10)

        # Test custom columns
        series = results.to_series(index="sampling_date", data="measurement_value")
        assert not series.empty
        assert series.name == "measurement_value"

        # Test invalid index column
        with pytest.raises(ValueError):
            results.to_series(index="invalid_column", data="measurement_value")

        # Test invalid data column
        with pytest.raises(ValueError):
            results.to_series(index="sampling_date", data="invalid_column")


def test_analysis_results_dataframe_sorting():
    """Test that analysis results DataFrame is sorted by sampling_date."""
    from pandas.api.types import is_datetime64_any_dtype as is_datetime

    client = SGUClient()

    # Create mock response with multiple dates
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[
            ("pH", "PH", 7.2),
            ("pH", "PH", 7.4),
            ("pH", "PH", 7.1),
        ],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        results = client.chemistry.get_analysis_results(limit=10)
        df = results.to_dataframe(sort_by_date=True)

        # Assert that it is sorted by 'sampling_date'
        assert is_datetime(df["sampling_date"])
        assert df["sampling_date"].is_monotonic_increasing


def test_pivot_by_parameter_with_nulls():
    """Test pivot_by_parameter handles null/missing values correctly."""
    client = SGUClient()

    # Create mock response with null values
    mock_response_data = create_mock_multiple_analysis_results_response(
        platsbeteckning="10001_1",
        parameters=[
            ("pH", "PH", 7.2),
            ("Nitrat", "NITRATE", None),  # Null value
        ],
    )

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        results = client.chemistry.get_analysis_results(limit=10)
        df_pivot = results.pivot_by_parameter()

        # Should still create DataFrame even with nulls
        assert df_pivot is not None
        assert "PH" in df_pivot.columns or "NITRATE" in df_pivot.columns


def test_empty_collection_to_dataframe():
    """Test converting empty collection to DataFrame returns empty DataFrame."""
    client = SGUClient()

    mock_response_data = create_mock_empty_chemistry_collection_response()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        results = client.chemistry.get_analysis_results(limit=1)
        df = results.to_dataframe()

        # Should return empty DataFrame, not error
        assert df.empty


def test_empty_collection_to_series():
    """Test converting empty collection to Series returns empty Series."""
    import pandas as pd

    client = SGUClient()

    mock_response_data = create_mock_empty_chemistry_collection_response()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        results = client.chemistry.get_analysis_results(limit=1)
        series = results.to_series()

        # Should return empty Series, not error
        assert isinstance(series, pd.Series)
        assert series.empty


def test_empty_collection_pivot():
    """Test pivoting empty collection returns empty DataFrame."""
    import pandas as pd

    client = SGUClient()

    mock_response_data = create_mock_empty_chemistry_collection_response()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(mock_response_data)

        results = client.chemistry.get_analysis_results(limit=1)
        df_pivot = results.pivot_by_parameter()

        # Should return empty DataFrame, not error
        assert isinstance(df_pivot, pd.DataFrame)
        assert df_pivot.empty
