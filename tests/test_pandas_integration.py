"""Tests for pandas integration and optional pandas dependency."""

import pytest

from sgu_client.utils.pandas_helpers import (
    PandasImportError,
    check_pandas_available,
    get_pandas,
    optional_pandas_method,
)


@pytest.fixture
def mock_pandas_missing(monkeypatch):
    """Fixture that makes pandas unavailable by mocking the import."""

    def mock_import(name, *args, **kwargs):
        if name == "pandas":
            raise ImportError("No module named 'pandas'")
        return __import__(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", mock_import)


def test_pandas_import_error_default_message():
    """Test PandasImportError with default feature name."""
    error = PandasImportError()
    assert "this feature requires pandas" in str(error)
    assert "sgu-client[recommended]" in str(error)


def test_pandas_import_error_custom_message():
    """Test PandasImportError with custom feature name."""
    error = PandasImportError("DataFrame conversion")
    assert "DataFrame conversion requires pandas" in str(error)
    assert "sgu-client[recommended]" in str(error)


def test_check_pandas_available_missing(mock_pandas_missing):  # noqa: ARG001
    """Test check_pandas_available when pandas is not installed."""
    with pytest.raises(PandasImportError) as exc_info:
        check_pandas_available("test feature")

    assert "test feature requires pandas" in str(exc_info.value)
    assert "sgu-client[recommended]" in str(exc_info.value)


def test_get_pandas_missing(mock_pandas_missing):  # noqa: ARG001
    """Test get_pandas when pandas is not installed."""
    with pytest.raises(PandasImportError) as exc_info:
        get_pandas()

    assert "pandas operations requires pandas" in str(exc_info.value)


def test_optional_pandas_method_decorator_missing(mock_pandas_missing):  # noqa: ARG001
    """Test optional_pandas_method decorator when pandas is missing."""

    @optional_pandas_method("test method")
    def dummy_method():
        return "should not reach here"

    with pytest.raises(PandasImportError) as exc_info:
        dummy_method()

    assert "test method requires pandas" in str(exc_info.value)


def test_optional_pandas_method_decorator_available():
    """Test optional_pandas_method decorator when pandas is available."""

    @optional_pandas_method("test method")
    def dummy_method():
        return "success"

    # This should work since pandas is available in test environment
    result = dummy_method()
    assert result == "success"


def test_optional_pandas_method_preserves_metadata():
    """Test that decorator preserves function metadata."""

    @optional_pandas_method("test method")
    def dummy_method():
        """A test method."""
        return "success"

    assert dummy_method.__name__ == "dummy_method"
    assert dummy_method.__doc__ == "A test method."


def test_base_response_to_dataframe_missing_pandas(monkeypatch):
    """Test SGUResponse.to_dataframe when pandas is not available."""
    from sgu_client.models.base import SGUResponse

    response = SGUResponse()

    # Mock check_pandas_available to raise our exception
    def mock_check_pandas(_feature):
        raise PandasImportError("to_dataframe() method")

    monkeypatch.setattr(
        "sgu_client.utils.pandas_helpers.check_pandas_available", mock_check_pandas
    )

    with pytest.raises(PandasImportError) as exc_info:
        response.to_dataframe()

    assert "to_dataframe() method requires pandas" in str(exc_info.value)
