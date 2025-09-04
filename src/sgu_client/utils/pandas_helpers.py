"""Pandas utilities with optional dependency handling."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd
else:
    pd = None


class PandasImportError(ImportError):
    """Raised when pandas functionality is used but pandas is not installed."""

    def __init__(self, feature: str = "this feature") -> None:
        super().__init__(
            f"{feature} requires pandas. Install it by installing the 'recommended' extras: "
            "`pip install 'sgu-client[recommended]'` or `uv add 'sgu-client[recommended]'`."
        )


def check_pandas_available(feature: str = "this feature") -> None:
    """Check if pandas is available and raise helpful error if not.

    Args:
        feature: Description of the feature that requires pandas

    Raises:
        PandasImportError: If pandas is not available
    """
    try:
        import pandas as pd  # noqa: F401
    except ImportError as err:
        raise PandasImportError(feature) from err


def get_pandas() -> Any:
    """Get pandas module with proper error handling.

    Returns:
        The pandas module

    Raises:
        PandasImportError: If pandas is not available
    """
    try:
        import pandas as pd

        return pd
    except ImportError as err:
        raise PandasImportError("pandas operations") from err


def optional_pandas_method(feature_name: str):
    """Decorator to mark methods that require pandas."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            check_pandas_available(feature_name)
            return func(*args, **kwargs)

        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__annotations__ = func.__annotations__

        return wrapper

    return decorator
