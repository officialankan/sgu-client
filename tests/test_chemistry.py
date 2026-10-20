"""Tests for chemistry module with mocked API responses (SGU v2 API)."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
import requests.exceptions
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
    CHEMISTRY_V2_BASE_URL,
    create_mock_analysis_result_collection_response,
    create_mock_analysis_result_feature,
    create_mock_empty_chemistry_collection_response,
    create_mock_multiple_analysis_results_response,
    create_mock_multiple_sampling_sites_response,
    create_mock_sampling_site_collection_response,
    create_mock_sampling_site_feature,
)


def create_mock_response(response_data, status_code=200):
    """Create a mock HTTP response object."""
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = status_code
    mock_response.json.return_value = response_data
    return mock_response


# Model parsing tests


def test_sampling_site_parses_v2_payload():
    """A v2 sampling site maps its Swedish API fields to typed English attributes."""
    site = SamplingSite(**create_mock_sampling_site_feature())

    props = site.properties
    assert props.national_site_id == 359366
    assert props.station_id == "TTK-442-M"
    assert props.site_name == "Lena"
    assert props.site_uuid == "c8942ea7-9708-4ba3-85c3-be4f84cd5e4b"
    assert props.county_code == "04"
    assert props.municipality == "FLEN"
    assert props.soil_type_description == "sand"
    assert props.pipe_height == 0.35
    assert props.first_sample_date == datetime(2021, 10, 6, tzinfo=UTC)
    assert props.analyses_csv_url is not None
    assert props.analyses_csv_url.endswith("&f=text/csv")
    assert site.geometry is not None
    assert site.geometry.coordinates == [16.68629857, 58.90889813]


def test_analysis_result_parses_v2_payload():
    """A v2 analysis result maps its Swedish API fields to typed English attributes."""
    result = AnalysisResult(**create_mock_analysis_result_feature())

    props = result.properties
    assert props.national_site_id == 359366
    assert props.site_name == "Lena"
    assert props.parameter_name == "Nitratkväve"
    assert props.parameter_id == "CH02/102"
    assert props.parameter_group == "Närsalter~Joner"
    assert props.measurement_value == 2.99
    assert props.unit == "mg.l-1"
    assert props.sampling_date == datetime(2021, 10, 6, tzinfo=UTC)
    assert props.method == "Beräknad från NO3"
    assert props.county == "SÖDERMANLANDS LÄN"


@pytest.mark.parametrize(
    ("lanskod", "expected"), [(4, "04"), (23, "23"), ("09", "09"), (None, None)]
)
def test_county_code_is_zero_padded_string(lanskod, expected):
    """County codes are normalised to two-digit strings on both models."""
    result = AnalysisResult(**create_mock_analysis_result_feature(lanskod=lanskod))
    site_feature = create_mock_sampling_site_feature()
    site_feature["properties"]["lanskod"] = lanskod
    site = SamplingSite(**site_feature)

    assert result.properties.county_code == expected
    assert site.properties.county_code == expected


# Client request tests


def test_get_sampling_sites_requests_v2_api():
    """Sampling sites are fetched from the v2 grundvattenkvalitet dataset."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_sampling_site_collection_response()
        )
        sites = client.chemistry.get_sampling_sites(limit=1)

    assert mock_request.call_args.kwargs["url"] == (
        f"{CHEMISTRY_V2_BASE_URL}collections/provplatser/items"
    )
    assert sites.features[0].properties.station_id == "TTK-442-M"


def test_get_analysis_results_requests_v2_api():
    """Analysis results are fetched from the v2 grundvattenkvalitet dataset."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_analysis_result_collection_response()
        )
        results = client.chemistry.get_analysis_results(limit=1)

    assert mock_request.call_args.kwargs["url"] == (
        f"{CHEMISTRY_V2_BASE_URL}collections/analysresultat/items"
    )
    assert results.features[0].properties.parameter_name == "Nitratkväve"


def test_get_results_by_site_with_national_site_id(caplog):
    """national_site_id is the first argument and filters results in one request."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_multiple_analysis_results_response(
                nationellt_provplatsid=359366
            )
        )
        results = client.chemistry.get_results_by_site(359366)

    assert mock_request.call_count == 1
    assert (
        mock_request.call_args.kwargs["params"]["filter"]
        == "nationellt_provplatsid=359366"
    )
    assert len(results.features) == 3
    assert "additional API request" not in caplog.text


@pytest.mark.parametrize(
    ("kwargs", "expected_lookup_filter"),
    [
        ({"site_id": "TTK-442-M"}, "platsbeteckning='TTK-442-M'"),
        ({"site_name": "Lena"}, "provplatsnamn='Lena'"),
    ],
)
def test_get_results_by_site_looks_up_national_site_id(
    caplog, kwargs, expected_lookup_filter
):
    """site_id/site_name are resolved to a national_site_id, with a warning."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.side_effect = [
            create_mock_response(create_mock_sampling_site_collection_response()),
            create_mock_response(create_mock_multiple_analysis_results_response()),
        ]
        results = client.chemistry.get_results_by_site(**kwargs)

    lookup_call, results_call = mock_request.call_args_list
    assert lookup_call.kwargs["url"].endswith("collections/provplatser/items")
    assert lookup_call.kwargs["params"]["filter"] == expected_lookup_filter
    assert results_call.kwargs["url"].endswith("collections/analysresultat/items")
    assert results_call.kwargs["params"]["filter"] == "nationellt_provplatsid=359366"
    assert len(results.features) == 3
    assert "additional API request" in caplog.text
    assert "national_site_id" in caplog.text


def test_get_results_by_site_unknown_site_id_raises():
    """A site_id that matches no sampling site raises a ValueError naming it."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_sampling_site_collection_response(sites=[])
        )
        with pytest.raises(ValueError, match="NOPE-1"):
            client.chemistry.get_results_by_site(site_id="NOPE-1")


def test_get_results_by_sites_with_national_site_ids():
    """A list of national_site_ids filters results with a single IN clause."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_multiple_analysis_results_response()
        )
        client.chemistry.get_results_by_sites([359366, 378865])

    assert mock_request.call_count == 1
    assert (
        mock_request.call_args.kwargs["params"]["filter"]
        == "nationellt_provplatsid in (359366, 378865)"
    )


def test_get_results_by_sites_with_site_ids(caplog):
    """A list of site_ids is resolved to national_site_ids in one lookup request."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.side_effect = [
            create_mock_response(create_mock_multiple_sampling_sites_response()),
            create_mock_response(create_mock_multiple_analysis_results_response()),
        ]
        client.chemistry.get_results_by_sites(site_id=["TTK-442-M", "SYD-681-C"])

    lookup_call, results_call = mock_request.call_args_list
    assert (
        lookup_call.kwargs["params"]["filter"]
        == "platsbeteckning in ('TTK-442-M', 'SYD-681-C')"
    )
    assert (
        results_call.kwargs["params"]["filter"]
        == "nationellt_provplatsid in (359366, 378865)"
    )
    assert "additional API request" in caplog.text


def test_get_results_by_sites_partial_lookup_raises():
    """If only some site_ids are found, a ValueError names the missing ones."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_multiple_sampling_sites_response()
        )
        with pytest.raises(ValueError, match="NOPE-1"):
            client.chemistry.get_results_by_sites(
                site_id=["TTK-442-M", "SYD-681-C", "NOPE-1"]
            )

    assert mock_request.call_count == 1


@pytest.mark.parametrize(
    ("kwargs", "expected_filter"),
    [
        ({}, "parameternamn='Bly'"),
        (
            {"national_site_id": 359366},
            "parameternamn='Bly' AND nationellt_provplatsid=359366",
        ),
        (
            {"national_site_id": [359366, 378865]},
            "parameternamn='Bly' AND nationellt_provplatsid in (359366, 378865)",
        ),
        (
            {"tmin": "2020-01-01", "tmax": "2021-01-01"},
            "parameternamn='Bly' AND provtagningsdatum >= '2020-01-01' "
            "AND provtagningsdatum <= '2021-01-01'",
        ),
    ],
)
def test_get_results_by_parameter_filters(kwargs, expected_filter):
    """Results are filtered on parameternamn, optionally by site and time."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_analysis_result_collection_response()
        )
        client.chemistry.get_results_by_parameter("Bly", **kwargs)

    assert mock_request.call_count == 1
    assert mock_request.call_args.kwargs["params"]["filter"] == expected_filter


def test_get_results_by_parameter_with_site_id(caplog):
    """A site_id filter is resolved to a national_site_id, like get_results_by_site."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.side_effect = [
            create_mock_response(create_mock_sampling_site_collection_response()),
            create_mock_response(create_mock_analysis_result_collection_response()),
        ]
        client.chemistry.get_results_by_parameter("Bly", site_id="TTK-442-M")

    assert (
        mock_request.call_args.kwargs["params"]["filter"]
        == "parameternamn='Bly' AND nationellt_provplatsid=359366"
    )
    assert "additional API request" in caplog.text


def test_get_results_by_parameter_multiple_site_identifiers_raises():
    """Only one kind of site identifier may be passed."""
    client = SGUClient()
    with pytest.raises(ValueError, match="Exactly one of 'national_site_id'"):
        client.chemistry.get_results_by_parameter(
            "Bly", national_site_id=359366, site_id="TTK-442-M"
        )


@pytest.mark.parametrize(
    ("kwargs", "expected_filter"),
    [
        ({"site_id": "TTK-442-M"}, "platsbeteckning='TTK-442-M'"),
        ({"site_name": "Lena"}, "provplatsnamn='Lena'"),
        ({"national_site_id": 359366}, "nationellt_provplatsid=359366"),
    ],
)
def test_get_sampling_site_by_name(caplog, kwargs, expected_filter):
    """A sampling site can be looked up by any identifier in a single request."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_sampling_site_collection_response()
        )
        site = client.chemistry.get_sampling_site_by_name(**kwargs)

    assert mock_request.call_count == 1
    assert mock_request.call_args.kwargs["params"]["filter"] == expected_filter
    assert site.properties.national_site_id == 359366
    assert "additional API request" not in caplog.text


@pytest.mark.parametrize(
    ("kwargs", "expected_filter"),
    [
        (
            {"site_id": ["TTK-442-M", "SYD-681-C"]},
            "platsbeteckning in ('TTK-442-M', 'SYD-681-C')",
        ),
        (
            {"site_name": ["Lena", "Tofta Bjärs"]},
            "provplatsnamn in ('Lena', 'Tofta Bjärs')",
        ),
        (
            {"national_site_id": [359366, 378865]},
            "nationellt_provplatsid in (359366, 378865)",
        ),
    ],
)
def test_get_sampling_sites_by_names(kwargs, expected_filter):
    """Multiple sampling sites can be looked up by any identifier."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_multiple_sampling_sites_response()
        )
        sites = client.chemistry.get_sampling_sites_by_names(**kwargs)

    assert mock_request.call_args.kwargs["params"]["filter"] == expected_filter
    assert [site.properties.national_site_id for site in sites.features] == [
        359366,
        378865,
    ]


# pandas integration tests


def test_sampling_sites_to_dataframe():
    """Sampling sites flatten to a DataFrame with geometry and parsed dates."""
    pd = pytest.importorskip("pandas")
    sites = SamplingSiteCollection(**create_mock_multiple_sampling_sites_response())

    df = sites.to_dataframe()

    assert list(df["feature_id"]) == ["provplatser.1", "provplatser.2"]
    assert list(df["national_site_id"]) == [359366, 378865]
    assert list(df["station_id"]) == ["TTK-442-M", "SYD-681-C"]
    assert df["longitude"].iloc[0] == 16.68629857
    assert df["county_code"].iloc[0] == "04"
    for column in ("established_date", "first_sample_date", "latest_sample_date"):
        assert pd.api.types.is_datetime64_any_dtype(df[column]), column
    assert df["first_sample_date"].iloc[0] == pd.Timestamp("2021-10-06", tz="UTC")


def test_analysis_results_to_dataframe():
    """Analysis results flatten to a DataFrame sorted by parsed sampling date."""
    pd = pytest.importorskip("pandas")
    results = AnalysisResultCollection(
        **create_mock_multiple_analysis_results_response(
            parameters=[("Klorid", "CH02/96", 8.3), ("pH", "CH11/62", 7.2)]
        )
    )
    results.features.reverse()

    df = results.to_dataframe()

    assert pd.api.types.is_datetime64_any_dtype(df["sampling_date"])
    assert list(df["parameter_name"]) == ["Klorid", "pH"]
    assert list(df["measurement_value"]) == [8.3, 7.2]
    assert list(df["county_code"]) == ["04", "04"]


def test_analysis_results_to_series():
    """to_series defaults to measurement values indexed by sampling date."""
    pd = pytest.importorskip("pandas")
    results = AnalysisResultCollection(
        **create_mock_multiple_analysis_results_response()
    )

    series = results.to_series()

    assert list(series.values) == [7.2, 2.99, 8.3]
    assert series.index[0] == pd.Timestamp("2020-01-01", tz="UTC")


def test_analysis_results_pivot_by_parameter():
    """pivot_by_parameter makes one column per SGU parameter name."""
    pytest.importorskip("pandas")
    results = AnalysisResultCollection(
        **create_mock_multiple_analysis_results_response()
    )

    df_pivot = results.pivot_by_parameter()

    assert sorted(df_pivot.columns) == ["Klorid", "Nitratkväve", "pH"]
    assert df_pivot["Nitratkväve"].dropna().tolist() == [2.99]


def test_get_results_by_site_with_datetime_objects():
    """datetime tmin/tmax are sent as ISO strings on provtagningsdatum."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_analysis_result_collection_response()
        )
        client.chemistry.get_results_by_site(
            359366,
            tmin=datetime(2020, 1, 1, tzinfo=UTC),
            tmax=datetime(2021, 1, 1, tzinfo=UTC),
        )

    assert mock_request.call_args.kwargs["params"]["filter"] == (
        "nationellt_provplatsid=359366"
        " AND provtagningsdatum >= '2020-01-01T00:00:00+00:00'"
        " AND provtagningsdatum <= '2021-01-01T00:00:00+00:00'"
    )


# Parameter validation tests

SITE_IDENTIFIER_ERROR = "Exactly one of 'national_site_id', 'site_id' or 'site_name'"


@pytest.mark.parametrize(
    ("method", "kwargs"),
    [
        ("get_sampling_site_by_name", {}),
        ("get_sampling_site_by_name", {"site_id": "TTK-442-M", "site_name": "Lena"}),
        ("get_sampling_sites_by_names", {}),
        ("get_sampling_sites_by_names", {"site_id": []}),
        (
            "get_sampling_sites_by_names",
            {"site_id": ["TTK-442-M"], "national_site_id": [359366]},
        ),
        ("get_results_by_site", {}),
        ("get_results_by_site", {"national_site_id": 359366, "site_id": "TTK-442-M"}),
        ("get_results_by_sites", {}),
        ("get_results_by_sites", {"national_site_id": []}),
        (
            "get_results_by_sites",
            {"site_id": ["TTK-442-M"], "site_name": ["Lena"]},
        ),
    ],
)
def test_site_identifier_validation(method, kwargs):
    """Site lookups require exactly one kind of site identifier."""
    client = SGUClient()
    with pytest.raises(ValueError, match=SITE_IDENTIFIER_ERROR):
        getattr(client.chemistry, method)(**kwargs)


def test_get_results_by_parameter_no_parameter():
    """get_results_by_parameter requires a parameter."""
    client = SGUClient()
    with pytest.raises(TypeError):
        client.chemistry.get_results_by_parameter()  # ty: ignore[missing-argument]


def test_get_results_by_site_multiple_sites_for_name_raises():
    """A site_name matching several sites is ambiguous for a single-site lookup."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_multiple_sampling_sites_response(
                sites=[("A-1", "Brunn", 1), ("B-2", "Brunn", 2)]
            )
        )
        with pytest.raises(ValueError, match="Multiple sites found"):
            client.chemistry.get_results_by_site(site_name="Brunn")


# Error condition tests


def test_api_timeout_error():
    """API timeout errors are raised as SGUTimeoutError."""
    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = requests.exceptions.ReadTimeout("Read timeout")

        client = SGUClient()
        with pytest.raises(SGUTimeoutError, match="Read timeout"):
            client.chemistry.get_sampling_sites()


def test_api_connection_error():
    """API connection errors are raised as SGUConnectionError."""
    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        client = SGUClient()
        with pytest.raises(SGUConnectionError, match="Connection failed"):
            client.chemistry.get_sampling_sites()


@pytest.mark.parametrize("status_code", [404, 500])
def test_api_error_status(status_code):
    """Non-2xx responses are raised as SGUAPIError."""
    with patch("requests.Session.request") as mock_request:
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = status_code
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "error page"
        mock_request.return_value = mock_response

        client = SGUClient()
        with pytest.raises(
            SGUAPIError, match=f"API request failed with status {status_code}"
        ):
            client.chemistry.get_sampling_sites()


def test_get_sampling_site_not_found():
    """An empty response for a single site ID raises ValueError."""
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_empty_chemistry_collection_response()
        )

        client = SGUClient()
        with pytest.raises(ValueError, match="Site .* not found"):
            client.chemistry.get_sampling_site("provplatser.0")


def test_get_analysis_result_not_found():
    """An empty response for a single result ID raises ValueError."""
    with patch("requests.Session.request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_empty_chemistry_collection_response()
        )

        client = SGUClient()
        with pytest.raises(ValueError, match="Result .* not found"):
            client.chemistry.get_analysis_result("analysresultat.0")


def test_get_sampling_site_by_id():
    """A single sampling site is fetched by its feature ID."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_sampling_site_collection_response()
        )
        site = client.chemistry.get_sampling_site("provplatser.1560")

    assert mock_request.call_args.kwargs["url"] == (
        f"{CHEMISTRY_V2_BASE_URL}collections/provplatser/items/provplatser.1560"
    )
    assert site.properties.station_id == "TTK-442-M"


def test_analysis_results_to_series_custom_columns():
    """to_series accepts custom columns and rejects unknown ones."""
    pytest.importorskip("pandas")
    results = AnalysisResultCollection(
        **create_mock_multiple_analysis_results_response()
    )

    series = results.to_series(index="sampling_date", data="parameter_name")
    assert list(series.values) == ["pH", "Nitratkväve", "Klorid"]
    assert series.name == "parameter_name"

    with pytest.raises(ValueError):
        results.to_series(index="invalid_column")
    with pytest.raises(ValueError):
        results.to_series(data="invalid_column")


def test_pivot_by_parameter_with_nulls():
    """pivot_by_parameter tolerates missing measurement values."""
    pytest.importorskip("pandas")
    results = AnalysisResultCollection(
        **create_mock_multiple_analysis_results_response(
            parameters=[("pH", "CH11/62", 7.2), ("Nitratkväve", "CH02/102", None)]
        )
    )

    df_pivot = results.pivot_by_parameter()

    assert df_pivot["pH"].dropna().tolist() == [7.2]


def test_empty_collections_convert_to_empty_pandas_objects():
    """Empty collections convert to empty DataFrames/Series without errors."""
    pd = pytest.importorskip("pandas")
    results = AnalysisResultCollection(
        **create_mock_empty_chemistry_collection_response()
    )
    sites = SamplingSiteCollection(**create_mock_empty_chemistry_collection_response())

    assert results.to_dataframe().empty
    assert sites.to_dataframe().empty
    assert isinstance(results.to_series(), pd.Series)
    assert results.to_series().empty
    assert results.pivot_by_parameter().empty


def test_analysis_results_to_dataframe_keeps_feature_id_and_result_id():
    """The feature ID and SGU's resultatid are separate DataFrame columns."""
    pytest.importorskip("pandas")
    results = AnalysisResultCollection(
        **create_mock_analysis_result_collection_response()
    )

    df = results.to_dataframe()

    assert df["feature_id"].iloc[0] == "analysresultat.1757"
    assert df["result_id"].iloc[0] == 5865282


@pytest.mark.parametrize(
    ("kwargs", "missing"),
    [
        ({"site_id": ["TTK-442-M", "NOPE-1"]}, "NOPE-1"),
        ({"site_name": ["Lena", "Nowhere"]}, "Nowhere"),
        ({"national_site_id": [359366, 1]}, "1"),
    ],
)
def test_get_sampling_sites_by_names_missing_sites_raises(kwargs, missing):
    """Sites that are not found are named in a ValueError, as for results."""
    client = SGUClient()

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_sampling_site_collection_response()
        )
        with pytest.raises(
            ValueError, match=f"No sampling sites found for .*{missing}"
        ):
            client.chemistry.get_sampling_sites_by_names(**kwargs)


def test_get_results_by_site_lookup_without_national_site_id_raises():
    """A looked-up site without a national_site_id raises instead of sending bad CQL."""
    client = SGUClient()
    site = create_mock_sampling_site_feature()
    site["properties"]["nationellt_provplatsid"] = None

    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_sampling_site_collection_response([site])
        )
        with pytest.raises(ValueError, match="no national_site_id"):
            client.chemistry.get_results_by_site(site_id="TTK-442-M")

    assert mock_request.call_count == 1


def test_get_analysis_results_filters_on_sampling_date():
    client = SGUClient()
    with patch.object(client.chemistry._client._session, "request") as mock_request:
        mock_request.return_value = create_mock_response(
            create_mock_empty_chemistry_collection_response()
        )
        client.chemistry.get_analysis_results(tmin="2020-01-01", tmax="2021-01-01")

    assert mock_request.call_args.kwargs["params"]["filter"] == (
        "provtagningsdatum >= '2020-01-01' AND provtagningsdatum <= '2021-01-01'"
    )
