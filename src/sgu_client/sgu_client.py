"""Main SGU Client class."""

from .client.base import BaseClient
from .client.levels.modeled import ModeledGroundwaterLevelsClient
from .client.levels.observed import ObservedGroundwaterLevelClient
from .config import SGUConfig


class SGUClient:
    """Main client for interacting with SGU API.

    This is the primary interface users will interact with.

    Example:
        >>> client = SGUClient()
        >>> data = client.groundwater.get_measurements(station_id="12345")
        >>> stations = client.groundwater.get_stations()

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
        self.observed_levels = ObservedGroundwaterLevelClient(self._base_client)
        self.modeled_levels = ModeledGroundwaterLevelsClient(self._base_client)

    def __enter__(self):
        """Context manager entry."""
        self._base_client.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._base_client.__exit__(exc_type, exc_val, exc_tb)
