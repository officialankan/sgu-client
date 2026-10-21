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
   SGUNotFoundError
   SGUAmbiguousError

Configuration
-------------

Pass an :class:`SGUConfig` to :class:`SGUClient` to change timeouts, retries or logging.
The configuration is immutable once created.

``timeout``, ``max_retries`` and ``user_agent`` configure the default
:class:`RequestsTransport`. A transport you pass to ``SGUClient(transport=...)`` doesn't
use them (see :doc:`client`).

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
   ├── SGUValidationError  data validation failed
   ├── SGUNotFoundError    a lookup matched nothing (also a ValueError)
   └── SGUAmbiguousError   a lookup expecting one feature matched several
                           (also a ValueError)

.. autoexception:: SGUClientError

.. autoexception:: SGUAPIError

.. autoexception:: SGUConnectionError

.. autoexception:: SGUTimeoutError

.. autoexception:: SGUValidationError

.. autoexception:: SGUNotFoundError

.. autoexception:: SGUAmbiguousError
