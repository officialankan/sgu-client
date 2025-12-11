"""Tests for automatic pagination functionality using mocks."""

from unittest.mock import Mock, patch

import pytest
from requests import Response

from sgu_client.client.base import BaseClient
from sgu_client.config import SGUConfig


@pytest.fixture
def client():
    """Create a base client for testing."""
    config = SGUConfig()  # Default config (no debug logging)
    return BaseClient(config)


def create_mock_response(features, number_returned, number_matched, status_code=200):
    """Create a mock response with specified pagination metadata."""
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = status_code
    mock_response.json.return_value = {
        "type": "FeatureCollection",
        "features": features,
        "numberReturned": number_returned,
        "numberMatched": number_matched,
        "totalFeatures": number_matched,
        "timeStamp": "2024-01-01T12:00:00Z",
        "links": [],
    }
    return mock_response


def create_mock_features(start_id, count):
    """Create mock GeoJSON features for testing."""
    return [
        {
            "type": "Feature",
            "id": f"feature.{i}",
            "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
            "properties": {"test_id": i},
        }
        for i in range(start_id, start_id + count)
    ]


def test_no_pagination_needed(client):
    """Test when pagination is not needed (all features returned)."""
    features = create_mock_features(1, 100)
    mock_response = create_mock_response(
        features=features, number_returned=100, number_matched=100
    )

    with patch.object(
        client._session, "request", return_value=mock_response
    ) as mock_request:
        result = client.get("/test")

    # Should return original response without pagination
    assert result["numberReturned"] == 100
    assert result["numberMatched"] == 100
    assert len(result["features"]) == 100
    assert mock_request.call_count == 1


def test_pagination_with_explicit_limit(client):
    """Test pagination when user requests more than API returns initially."""
    # First response: 50K out of 60K requested
    first_features = create_mock_features(1, 50000)
    first_response = create_mock_response(
        features=first_features,
        number_returned=50000,
        number_matched=8000000,  # Large number like real API
    )

    # Second response: remaining 10K features
    second_features = create_mock_features(50001, 10000)
    second_response = create_mock_response(
        features=second_features, number_returned=10000, number_matched=8000000
    )

    with patch.object(
        client._session, "request", side_effect=[first_response, second_response]
    ) as mock_request:
        result = client.get("/test", params={"limit": 60000})

    # Should combine both responses
    assert result["numberReturned"] == 60000
    assert result["numberMatched"] == 8000000  # Preserved from original
    assert len(result["features"]) == 60000

    # Verify features from both pages are present
    feature_ids = [f["properties"]["test_id"] for f in result["features"]]
    assert min(feature_ids) == 1
    assert max(feature_ids) == 60000

    # Should have made exactly 2 requests
    assert mock_request.call_count == 2

    # Check second request parameters
    second_call = mock_request.call_args_list[1]
    assert second_call[1]["params"]["startIndex"] == 50000
    assert second_call[1]["params"]["limit"] == 10000


def test_pagination_default_50k_limit(client):
    """Test pagination with default 50K safety limit when no user limit specified."""
    # Response with more data available than default limit
    features = create_mock_features(1, 50000)
    mock_response = create_mock_response(
        features=features,
        number_returned=50000,
        number_matched=8000000,  # Lots more available
    )

    with patch.object(
        client._session, "request", return_value=mock_response
    ) as mock_request:
        result = client.get("/test")  # No explicit limit

    # Should NOT paginate beyond 50K when no user limit specified
    assert result["numberReturned"] == 50000
    assert len(result["features"]) == 50000
    assert mock_request.call_count == 1


def test_pagination_multiple_pages(client):
    """Test pagination across multiple pages (more than 2 requests)."""
    # Simulate requesting 250 features in pages of 100
    responses = []
    for page in range(3):
        start_id = page * 100 + 1
        count = 50 if page == 2 else 100  # Last page has only 50
        features = create_mock_features(start_id, count)
        responses.append(
            create_mock_response(
                features=features, number_returned=count, number_matched=250
            )
        )

    with patch.object(
        client._session, "request", side_effect=responses
    ) as mock_request:
        result = client.get("/test", params={"limit": 250})

    assert result["numberReturned"] == 250
    assert len(result["features"]) == 250
    assert mock_request.call_count == 3

    # Verify all features are present in correct order
    feature_ids = [f["properties"]["test_id"] for f in result["features"]]
    assert feature_ids == list(range(1, 251))


def test_pagination_with_unknown_number_matched(client):
    """Test that pagination is skipped when numberMatched is 'unknown'."""
    features = create_mock_features(1, 10)
    mock_response = create_mock_response(
        features=features,
        number_returned=10,
        number_matched="unknown",  # String value like modeled API
    )

    with patch.object(
        client._session, "request", return_value=mock_response
    ) as mock_request:
        result = client.get("/test")

    # Should not attempt pagination
    assert result["numberReturned"] == 10
    assert result["numberMatched"] == "unknown"
    assert len(result["features"]) == 10
    assert mock_request.call_count == 1


def test_pagination_with_null_number_matched(client):
    """Test that pagination is skipped when numberMatched is null/None."""
    features = create_mock_features(1, 10)

    # Create response without numberMatched field
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "type": "FeatureCollection",
        "features": features,
        "numberReturned": 10,
        # numberMatched missing
    }

    with patch.object(
        client._session, "request", return_value=mock_response
    ) as mock_request:
        result = client.get("/test")

    # Should not attempt pagination
    assert result["numberReturned"] == 10
    assert len(result["features"]) == 10
    assert mock_request.call_count == 1


def test_pagination_preserves_other_response_fields(client):
    """Test that pagination preserves non-features fields from original response."""
    # First response with extra metadata
    first_features = create_mock_features(1, 100)
    first_response = Mock(spec=Response)
    first_response.ok = True
    first_response.status_code = 200
    first_response.json.return_value = {
        "type": "FeatureCollection",
        "features": first_features,
        "numberReturned": 100,
        "numberMatched": 150,
        "timeStamp": "2024-01-01T12:00:00Z",
        "links": [{"rel": "self", "href": "/test"}],
        "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
    }

    # Second response
    second_features = create_mock_features(101, 50)
    second_response = create_mock_response(
        features=second_features, number_returned=50, number_matched=150
    )

    with patch.object(
        client._session, "request", side_effect=[first_response, second_response]
    ) as mock_request:
        result = client.get("/test", params={"limit": 150})

    # Should preserve original metadata
    assert result["timeStamp"] == "2024-01-01T12:00:00Z"
    assert result["links"] == [{"rel": "self", "href": "/test"}]
    assert result["crs"] == {"type": "name", "properties": {"name": "EPSG:4326"}}

    # But update pagination-specific fields
    assert result["numberReturned"] == 150
    assert len(result["features"]) == 150
    assert mock_request.call_count == 2


def test_pagination_stops_on_empty_page(client):
    """Test that pagination stops when a page returns no features."""
    # First response claims more data available
    first_features = create_mock_features(1, 100)
    first_response = create_mock_response(
        features=first_features, number_returned=100, number_matched=200
    )

    # Second response returns empty (no more data actually available)
    second_response = create_mock_response(
        features=[], number_returned=0, number_matched=200
    )

    with patch.object(
        client._session, "request", side_effect=[first_response, second_response]
    ) as mock_request:
        result = client.get("/test", params={"limit": 200})

    # Should stop pagination after empty page
    assert result["numberReturned"] == 100  # Only first page
    assert len(result["features"]) == 100
    assert mock_request.call_count == 2


def test_pagination_error_handling(client):
    """Test that pagination errors are properly raised."""
    # First response succeeds
    first_features = create_mock_features(1, 100)
    first_response = create_mock_response(
        features=first_features, number_returned=100, number_matched=200
    )

    # Second request fails
    second_response = Mock(spec=Response)
    second_response.ok = False
    second_response.status_code = 500
    second_response.json.return_value = {"error": "Server error"}

    with (
        patch.object(
            client._session, "request", side_effect=[first_response, second_response]
        ),
        pytest.raises(Exception, match="Pagination request failed"),
    ):
        client.get("/test", params={"limit": 200})


def test_non_feature_collection_not_paginated(client):
    """Test that non-FeatureCollection responses are not paginated."""
    # Non-GeoJSON response
    mock_response = Mock(spec=Response)
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "message": "Hello World",
        "numberReturned": 10,
        "numberMatched": 100,
    }

    with patch.object(
        client._session, "request", return_value=mock_response
    ) as mock_request:
        result = client.get("/test")

    # Should return as-is without pagination
    assert result == {
        "message": "Hello World",
        "numberReturned": 10,
        "numberMatched": 100,
    }
    assert mock_request.call_count == 1


def test_post_request_not_paginated(client):
    """Test that POST requests are not paginated."""
    features = create_mock_features(1, 100)
    mock_response = create_mock_response(
        features=features, number_returned=100, number_matched=200
    )

    with patch.object(
        client._session, "request", return_value=mock_response
    ) as mock_request:
        result = client.post("/test", data={"query": "test"})

    # Should not attempt pagination for POST
    assert result["numberReturned"] == 100
    assert len(result["features"]) == 100
    assert mock_request.call_count == 1
