"""Main SGU Client class."""

from .client.base import BaseClient
from .client.chemistry import GroundwaterChemistryClient
from .client.levels import LevelsClient
from .config import SGUConfig
from .transport import Transport


class SGUClient:
    """Main client for interacting with SGU API.

    This is the primary interface users will interact with.

    Use it as a context manager so the HTTP session is closed when you are done.
    If the client has to outlive a ``with`` block, call :meth:`close` yourself.

    Example:
        >>> with SGUClient() as client:
        ...     stations = client.levels.observed.get_stations()
        ...     measurements = client.levels.observed.get_measurements()

        >>> # With custom config
        >>> config = SGUConfig(timeout=60, log_level="DEBUG")
        >>> with SGUClient(config=config) as client:
        ...     stations = client.levels.observed.get_stations()
    """

    def __init__(
        self, config: SGUConfig | None = None, *, transport: Transport | None = None
    ):
        """Initialize the SGU client.

        Args:
            config: Configuration object. If None, uses default config.
            transport: Where requests go. If None, the client talks to SGU over the
                network with a :class:`~sgu_client.RequestsTransport` built from
                ``config``, and closes it in :meth:`close`. A transport you pass in
                is yours to close, and the network settings in ``config``
                (``timeout``, ``max_retries``, ``user_agent``) don't apply to it.
        """
        self._base_client = BaseClient(config, transport)

        # Initialize sub-clients
        self.levels = LevelsClient(self._base_client)
        self.chemistry = GroundwaterChemistryClient(self._base_client)

    def close(self) -> None:
        """Close the underlying HTTP session and its pooled connections.

        Called automatically when the client is used as a context manager. Call it
        yourself when you create the client without a ``with`` block.
        """
        self._base_client.close()

    def __enter__(self):
        """Context manager entry.

        Returns:
            The SGU client instance for use in with statements
        """
        self._base_client.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clean up resources.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        self.close()
