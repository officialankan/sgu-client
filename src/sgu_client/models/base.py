"""Base model classes for SGU Client."""

from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict


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

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame.

        Returns:
            DataFrame with the data
        """
        # This will be implemented by subclasses
        raise NotImplementedError("Subclasses must implement to_dataframe()")
