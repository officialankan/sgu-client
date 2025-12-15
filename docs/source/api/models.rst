Data Models
===========

Base Model Classes
------------------

The :class:`~sgu_client.models.base.SGUBaseModel` and :class:`~sgu_client.models.base.SGUResponse` classes provide the foundation for all data models.

.. automodule:: sgu_client.models.base
   :members:
   :undoc-members:
   :show-inheritance:

Shared Types
------------

The :mod:`~sgu_client.models.shared` module provides common data structures used across multiple API domains.

**GeoJSON Support:**

The library provides full GeoJSON geometry support:

- :class:`~sgu_client.models.shared.Point` - Point geometry
- :class:`~sgu_client.models.shared.LineString` - Line geometry
- :class:`~sgu_client.models.shared.Polygon` - Polygon geometry
- :class:`~sgu_client.models.shared.MultiPoint` - Multi-point geometry
- :class:`~sgu_client.models.shared.MultiLineString` - Multi-line geometry
- :class:`~sgu_client.models.shared.MultiPolygon` - Multi-polygon geometry

**Other Shared Types:**

- :class:`~sgu_client.models.shared.Link` - Hypermedia links in responses
- :class:`~sgu_client.models.shared.CRS` - Coordinate reference system metadata

.. automodule:: sgu_client.models.shared
   :members:
   :undoc-members:
   :show-inheritance:

Domain-Specific Models
-----------------------

For domain-specific data models, see:

- :doc:`levels` - Observed and modeled groundwater level models
- :doc:`chemistry` - Groundwater chemistry measurement models

Working with Models
-------------------

**Type Hints Example:**

.. code-block:: python

   from sgu_client import SGUClient

   client = SGUClient()
   stations = client.levels.observed.get_stations(limit=5)

   # full type hints for IDE autocomplete
   for station in stations.features:
       print(f"Station: {station.properties.station_name}")
       print(f"Municipality: {station.properties.municipality}")
       print(f"Coordinates: {station.geometry.coordinates}")

**DataFrame Conversion:**

.. code-block:: python

   # convert to pandas DataFrame (requires pandas)
   df = stations.to_dataframe()

   # geometry and properties are automatically flattened
   print(df.columns)  # station_id, longitude, latitude, municipality, etc.

See Also
--------

- :doc:`core` - Core client that returns these models
- :doc:`utilities` - pandas integration utilities
