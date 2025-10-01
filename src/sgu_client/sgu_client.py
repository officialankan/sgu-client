"""Main SGU Client class."""

from .client.base import BaseClient
from .client.chemistry import GroundwaterChemistryClient
from .client.levels import LevelsClient
from .config import SGUConfig


class SGUClient:
    """Main client for interacting with SGU API.

    This is the primary interface users will interact with.

    Example:
        >>> client = SGUClient()
        >>> stations = client.levels.observed.get_stations()
        >>> measurements = client.levels.observed.get_measurements()

        >>> # With custom config
        >>> config = SGUConfig(timeout=60, debug=True)
        >>> client = SGUClient(config=config)
    """

    def __init__(self, config: SGUConfig | None = None):
        """Initialize the SGU client.

        Args:
            config: Configuration object. If None, uses default config.
        """
        self._base_client = BaseClient(config)

        # Initialize sub-clients
        self.levels = LevelsClient(self._base_client)
        self.chemistry = GroundwaterChemistryClient(self._base_client)

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
        self._base_client.__exit__(exc_type, exc_val, exc_tb)
