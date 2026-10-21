"""Base model classes for SGU Client."""

from typing import Any

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
        # Allow instantiation by both field names and aliases
        validate_by_name=True,
        validate_by_alias=True,
    )


class SGUResponse(SGUBaseModel):
    """Base response wrapper for SGU API responses."""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()
