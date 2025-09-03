"""Levels client module."""

from .modeled import ModeledGroundwaterLevelsClient
from .observed import ObservedGroundwaterLevelClient


class LevelsClient:
    """Client for accessing groundwater level data.

    Provides access to both observed and modeled groundwater levels
    through a hierarchical API structure.

    Example:
        >>> client = SGUClient()
        >>> stations = client.levels.observed.get_stations()
        >>> measurements = client.levels.modeled.get_measurements()
    """

    def __init__(self, base_client):
        """Initialize the levels client.

        Args:
            base_client: The base HTTP client instance.
        """
        self.observed = ObservedGroundwaterLevelClient(base_client)
        self.modeled = ModeledGroundwaterLevelsClient(base_client)


__all__ = ["LevelsClient"]
