Core API
========

The core API provides the main client interface, configuration management, and exception handling for the sgu-client library.

Main Client
-----------

The :class:`~sgu_client.sgu_client.SGUClient` is the primary entry point for all API interactions. It provides a hierarchical interface to access different data domains.

**Usage Example:**

.. code-block:: python

   from sgu_client import SGUClient, SGUConfig

   # Basic usage
   client = SGUClient()

   # With custom configuration
   config = SGUConfig(timeout=60, debug=True, max_retries=5)
   client = SGUClient(config=config)

   # Using context manager
   with SGUClient() as client:
       stations = client.levels.observed.get_stations()

**API Documentation:**

.. automodule:: sgu_client.sgu_client
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
-------------

The :class:`~sgu_client.config.SGUConfig` class manages all configuration options for the SGU client, including API endpoints, timeouts, retry behavior, and logging.

**Configuration Options:**

- **timeout**: Request timeout in seconds (default: 30)
- **max_retries**: Maximum number of retry attempts (default: 3)
- **debug**: Enable debug logging (default: False)
- **base_url**: Override default API base URL (advanced usage)

.. automodule:: sgu_client.config
   :members:
   :undoc-members:
   :show-inheritance:

Exceptions
----------

The library provides specific exception classes for different error scenarios, all inheriting from :class:`~sgu_client.exceptions.SGUClientError`.

**Exception Hierarchy:**

- :class:`~sgu_client.exceptions.SGUClientError` - Base exception
- :class:`~sgu_client.exceptions.APIError` - API-related errors
- :class:`~sgu_client.exceptions.ValidationError` - Data validation errors
- :class:`~sgu_client.exceptions.NetworkError` - Network communication errors

.. automodule:: sgu_client.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Base Client
-----------

The :class:`~sgu_client.client.base.BaseClient` provides low-level HTTP communication with retry logic and error handling. Most users won't interact with this directly.

.. automodule:: sgu_client.client.base
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------

- :doc:`levels` - Groundwater levels API using this core infrastructure
- :doc:`chemistry` - Groundwater chemistry API using this core infrastructure
