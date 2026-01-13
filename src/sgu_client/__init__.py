"""SGU Client - Python library for accessing SGU groundwater data."""

from .config import SGUConfig
from .exceptions import (
    SGUAPIError,
    SGUClientError,
    SGUConnectionError,
    SGUTimeoutError,
    SGUValidationError,
)
from .sgu_client import SGUClient

__version__ = "0.4.3"
__all__ = [
    "SGUAPIError",
    "SGUClient",
    "SGUClientError",
    "SGUConfig",
    "SGUConnectionError",
    "SGUTimeoutError",
    "SGUValidationError",
]
