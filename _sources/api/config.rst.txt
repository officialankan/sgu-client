Configuration & exceptions
==========================

.. currentmodule:: sgu_client

.. autosummary::
   :nosignatures:

   SGUConfig
   SGUClientError
   SGUAPIError
   SGUConnectionError
   SGUTimeoutError
   SGUValidationError

Configuration
-------------

Pass an :class:`SGUConfig` to :class:`SGUClient` to change timeouts, retries or logging.
The configuration is immutable once created.

.. autopydantic_model:: SGUConfig

Exceptions
----------

All exceptions raised by the client inherit from :class:`SGUClientError`, so catching it
handles every client error:

.. code-block:: text

   SGUClientError
   ├── SGUAPIError         the API returned an error response
   ├── SGUConnectionError  the connection to the API failed
   ├── SGUTimeoutError     the request timed out
   └── SGUValidationError  data validation failed

.. autoexception:: SGUClientError

.. autoexception:: SGUAPIError

.. autoexception:: SGUConnectionError

.. autoexception:: SGUTimeoutError

.. autoexception:: SGUValidationError
