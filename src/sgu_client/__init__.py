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
from .transport import RequestsTransport, Transport, TransportResponse

__version__ = "0.7.0"
__all__ = [
    "RequestsTransport",
    "SGUAPIError",
    "SGUAmbiguousError",
    "SGUClient",
    "SGUClientError",
    "SGUConfig",
    "SGUConnectionError",
    "SGUNotFoundError",
    "SGUTimeoutError",
    "SGUValidationError",
    "Transport",
    "TransportResponse",
]
