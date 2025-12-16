"""Configuration management for SGU Client."""

import logging

from pydantic import BaseModel, ConfigDict, Field

# Track if logging has been configured to avoid duplicate configuration
_logging_configured = False


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

    # Logging settings
    log_level: str | int | None = Field(
        default="WARNING",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL or numeric value). "
        "Set to None to disable logging configuration and manage it yourself.",
    )

    model_config = ConfigDict(
        frozen=True,  # Make config immutable
        extra="forbid",  # Don't allow extra fields
    )


def setup_logging(log_level: str | int | None) -> None:
    """Configure logging for the SGU client.

    This function sets up logging with a standard format that includes
    timestamp, logger name, level, and message. It uses a singleton pattern
    to ensure logging is only configured once per process.

    Args:
        log_level: Logging level to use. Can be:
            - String: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
            - Integer: logging.DEBUG, logging.INFO, etc.
            - None: Skip logging configuration (user manages their own logging)

    Example:
        >>> setup_logging("DEBUG")
        >>> setup_logging(logging.INFO)
        >>> setup_logging(None)  # Don't configure logging
    """
    global _logging_configured

    # If log_level is None, don't configure logging
    if log_level is None:
        return

    # Only configure logging once
    if _logging_configured:
        return

    # Convert string log levels to uppercase for consistency
    if isinstance(log_level, str):
        log_level = log_level.upper()

    # Configure logging with standard format
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,  # Override any existing configuration
    )

    _logging_configured = True
