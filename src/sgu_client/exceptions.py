"""Custom exceptions for SGU Client."""


class SGUClientError(Exception):
    """Base exception for all SGU client errors."""

    pass


class SGUAPIError(SGUClientError):
    """Raised when the SGU API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class SGUConnectionError(SGUClientError):
    """Raised when connection to SGU API fails."""

    pass


class SGUTimeoutError(SGUClientError):
    """Raised when a request to SGU API times out."""

    pass


class SGUValidationError(SGUClientError):
    """Raised when data validation fails."""

    pass
