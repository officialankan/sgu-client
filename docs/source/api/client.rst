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
