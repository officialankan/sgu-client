Client
======

.. currentmodule:: sgu_client

:class:`SGUClient` is the entry point for every request. Endpoints are grouped by domain
on its attributes:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Attribute
     - Client
   * - ``client.levels.observed``
     - :class:`~sgu_client.client.levels.observed.ObservedGroundwaterLevelClient` (:doc:`observed`)
   * - ``client.levels.modeled``
     - :class:`~sgu_client.client.levels.modeled.ModeledGroundwaterLevelClient` (:doc:`modeled`)
   * - ``client.chemistry``
     - :class:`~sgu_client.client.chemistry.chemistry.GroundwaterChemistryClient` (:doc:`chemistry`)

See :doc:`/user_guide/getting_started` for an introduction.

SGUClient
---------

.. autoclass:: SGUClient
   :special-members: __init__, __enter__, __exit__

LevelsClient
------------

.. autoclass:: sgu_client.client.levels.LevelsClient

Transports
----------

Every request goes through a :class:`Transport`. By default that's a
:class:`RequestsTransport`, which talks to SGU over the network using the ``timeout``,
``max_retries`` and ``user_agent`` from :class:`SGUConfig`.

Pass your own transport to serve responses from somewhere else, for example canned
pages in your tests. A transport has one method, ``fetch``, which returns the status and
body of one response; the client still handles errors, JSON and pagination:

.. code-block:: python

   import json

   from sgu_client import SGUClient, TransportResponse

   class CannedTransport:
       def __init__(self, page: dict):
           self.page = page

       def fetch(self, url, params):
           return TransportResponse(200, json.dumps(self.page))

   client = SGUClient(transport=CannedTransport(my_station_page))
   stations = client.levels.observed.get_stations()

A transport you pass in is yours to close; :meth:`SGUClient.close` only closes the
transport the client created.

.. autoclass:: Transport
   :members: fetch

.. autoclass:: TransportResponse

.. autoclass:: RequestsTransport
   :members: fetch, close
