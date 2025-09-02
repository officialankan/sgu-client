"""Base model classes for SGU Client."""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    import pandas as pd

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None


class SGUBaseModel(BaseModel):
    """Base model for all SGU data structures."""

    model_config = ConfigDict(
        # Allow extra fields in case SGU API adds new fields
        extra="allow",
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Validate assignments
        validate_assignment=True,
    )


class SGUResponse(SGUBaseModel):
    """Base response wrapper for SGU API responses."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def to_dataframe(self) -> "pd.DataFrame | None":
        """Convert to pandas DataFrame if pandas is available.

        Returns:
            DataFrame if pandas is installed, None otherwise

        Raises:
            ImportError: If pandas is not available
        """
        if not HAS_PANDAS:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install with: uv add 'sgu-client[recommended]'"
            )

        # This will be implemented by subclasses
        raise NotImplementedError("Subclasses must implement to_dataframe()")
