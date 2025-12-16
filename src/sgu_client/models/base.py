"""Base model classes for SGU Client."""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict

from sgu_client.utils.pandas_helpers import optional_pandas_method

if TYPE_CHECKING:
    import pandas as pd


class SGUBaseModel(BaseModel):
    """Base model for all SGU data structures."""

    model_config = ConfigDict(
        # Allow extra fields in case SGU API adds new fields
        extra="allow",
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Validate assignments
        validate_assignment=True,
        # Allow instantiation by both field names and aliases
        validate_by_name=True,
        validate_by_alias=True,
    )


class SGUResponse(SGUBaseModel):
    """Base response wrapper for SGU API responses."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    @optional_pandas_method("to_dataframe() method")
    def to_dataframe(self) -> "pd.DataFrame":
        """Convert to pandas DataFrame.

        Returns:
            DataFrame with the data

        Examples:

            This is an abstract method that must be implemented by subclasses.
            Use concrete collection classes instead:

            >>> from sgu_client import SGUClient
            >>> client = SGUClient()
            >>> # Use specific collection types like GroundwaterStationCollection
            >>> stations = client.levels.observed.get_stations(limit=5)
            >>> df = stations.to_dataframe()  # This works!
        """
        # This will be implemented by subclasses
        raise NotImplementedError("Subclasses must implement to_dataframe()")
