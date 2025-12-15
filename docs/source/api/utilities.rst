Utilities
=========

The utilities module provides helper functions for data conversion and manipulation, primarily focused on pandas integration.

Overview
--------

The utilities module currently provides pandas integration helpers that enable conversion of API responses to pandas DataFrames. This is an optional feature requiring pandas installation.

pandas Integration
------------------

The :mod:`~sgu_client.utils.pandas_helpers` module provides decorators and utilities for converting Pydantic models to pandas DataFrames.

**Installation:**

To use pandas features, install with the recommended extras:

.. code-block:: bash

   pip install "sgu-client[recommended]"

**Usage Example:**

.. code-block:: python

   from sgu_client import SGUClient

   client = SGUClient()

   # Get data
   measurements = client.levels.observed.get_measurements(limit=1000)

   # Convert to DataFrame
   df = measurements.to_dataframe()

   # Now you can use pandas for analysis
   print(df.describe())
   print(df.groupby('station_id')['water_level'].mean())

**Features:**

- Automatic flattening of nested GeoJSON structures
- Geometry coordinates expanded to separate columns (longitude, latitude)
- Properties flattened to top-level DataFrame columns
- Datetime parsing for temporal analysis
- Optional dependency - graceful error if pandas not installed

API Documentation
-----------------

.. automodule:: sgu_client.utils.pandas_helpers
   :members:
   :undoc-members:
   :show-inheritance:

DataFrame Conversion Details
-----------------------------

When converting API responses to DataFrames:

1. **GeoJSON Features**: Each feature becomes a DataFrame row
2. **Geometry**: Coordinates extracted to ``longitude``, ``latitude`` columns (and ``altitude`` if 3D)
3. **Properties**: All properties flattened to top-level columns
4. **Metadata**: Collection-level metadata (links, timestamps) excluded

**Example Structure:**

.. code-block:: python

   # Original GeoJSON structure
   {
       "type": "FeatureCollection",
       "features": [
           {
               "type": "Feature",
               "geometry": {"type": "Point", "coordinates": [15.5, 58.3]},
               "properties": {"station_id": "95_2", "water_level": 45.3}
           }
       ]
   }

   # Converted DataFrame
   #    longitude  latitude  station_id  water_level
   # 0       15.5      58.3        95_2         45.3

See Also
--------

- :doc:`models` - Data models that support DataFrame conversion
- :doc:`levels` - Levels API examples with DataFrame conversion
- :doc:`chemistry` - Chemistry API examples with DataFrame conversion
