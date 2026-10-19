Shared models
=============

.. currentmodule:: sgu_client.models

Building blocks shared by the domain models. Domain-specific models are documented
next to their client: :doc:`observed`, :doc:`modeled` and :doc:`chemistry`.

.. autosummary::
   :nosignatures:

   ~base.SGUBaseModel
   ~base.SGUResponse
   ~shared.Point
   ~shared.MultiPoint
   ~shared.LineString
   ~shared.Polygon
   ~shared.MultiPolygon
   ~shared.Link
   ~shared.CRS

Base classes
------------

Every response collection inherits from :class:`~sgu_client.models.base.SGUResponse`.
Models accept both the English field names and the Swedish API aliases, and keep any
extra fields SGU adds in the future.

.. automodule:: sgu_client.models.base

GeoJSON types
-------------

.. automodule:: sgu_client.models.shared
