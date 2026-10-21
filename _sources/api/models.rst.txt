Shared models
=============

.. currentmodule:: sgu_client.models

Building blocks shared by the domain models. Domain-specific models are documented
next to their client: :doc:`observed`, :doc:`modeled` and :doc:`chemistry`.

.. autosummary::
   :nosignatures:

   ~features.FeatureCollection
   ~features.TimeSeriesCollection
   ~features.Feature
   ~base.SGUBaseModel
   ~base.SGUResponse
   ~shared.Point
   ~shared.MultiPoint
   ~shared.LineString
   ~shared.Polygon
   ~shared.MultiPolygon
   ~shared.Link
   ~shared.CRS

Collections and features
------------------------

Every collection model inherits from
:class:`~sgu_client.models.features.FeatureCollection`, which owns the GeoJSON fields
and the conversion to a DataFrame. Collections with a date per feature (measurements,
modeled levels and analysis results) inherit from
:class:`~sgu_client.models.features.TimeSeriesCollection`, which adds sorting by date
and ``to_series()``. See :doc:`/user_guide/pandas` for how the collections'
DataFrames differ.

.. automodule:: sgu_client.models.features

Base classes
------------

Models accept both the English field names and the Swedish API aliases, and keep any
extra fields SGU adds in the future.

.. automodule:: sgu_client.models.base

GeoJSON types
-------------

.. automodule:: sgu_client.models.shared
