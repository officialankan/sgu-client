"""SGU Client - Python library for accessing SGU groundwater data."""

from .config import SGUConfig
from .exceptions import (
    SGUAmbiguousError,
    SGUAPIError,
    SGUClientError,
    SGUConnectionError,
    SGUNotFoundError,
    SGUTimeoutError,
    SGUValidationError,
)
from .sgu_client import SGUClient

__version__ = "0.6.0"
__all__ = [
    "SGUAPIError",
    "SGUAmbiguousError",
    "SGUClient",
    "SGUClientError",
    "SGUConfig",
    "SGUConnectionError",
    "SGUNotFoundError",
    "SGUTimeoutError",
    "SGUValidationError",
]
