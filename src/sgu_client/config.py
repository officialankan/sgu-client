"""Configuration management for SGU Client."""

from pydantic import BaseModel, ConfigDict, Field


class SGUConfig(BaseModel):
    """Configuration settings for SGU API client."""

    # HTTP settings
    base_url: str = Field(
        default="https://api.sgu.se/oppnadata/grundvattennivaer-observerade/ogc/features/v1/",
        description="Base URL for SGU API",
    )
    timeout: float = Field(
        default=30.0, ge=1.0, description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3, ge=0, description="Maximum number of retry attempts"
    )

    # Request settings
    user_agent: str = Field(
        default="sgu-client/0.1.0", description="User-Agent header for requests"
    )

    # Debug settings
    debug: bool = Field(default=False, description="Enable debug logging")

    model_config = ConfigDict(
        frozen=True,  # Make config immutable
        extra="forbid",  # Don't allow extra fields
    )
