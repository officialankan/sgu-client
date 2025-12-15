Groundwater Levels API
======================

The groundwater levels API provides access to both observed measurements from monitoring stations and modeled predictions. This page documents both the client interfaces and the data models used for groundwater level data.

Overview
--------

The levels API is accessed through ``client.levels`` and provides two main sub-clients:

- **Observed**: Real measurements from groundwater monitoring stations
- **Modeled**: Predicted groundwater levels from the SGU-HYPE model

**Quick Example:**

.. code-block:: python

   from sgu_client import SGUClient

   client = SGUClient()

   # get observed data
   stations = client.levels.observed.get_stations(
       bbox=[12.0, 55.0, 16.0, 58.0],
       limit=50
   ) 
   measurements = client.levels.observed.get_measurements_by_names(
       [station.properties.station_id for station in stations.features],
       datetime="2023-01-01/2024-01-01",
       limit=1000
   )
   df_meas = measurements.to_dataframe()

   # get modeled data
   areas = client.levels.modeled.get_areas(
      bbox=[12.0, 55.0, 16.0, 58.0],
      limit=10
   )
   predictions = client.levels.modeled.get_levels_by_areas(
      [area.properties.area_id for area in areas.features],
      limit=100
   )
   df_pred = predictions.to_dataframe()

Observed Groundwater Levels
----------------------------

Client Interface
~~~~~~~~~~~~~~~~

The :class:`~sgu_client.client.levels.observed.ObservedGroundwaterLevelClient` provides methods to query monitoring stations and retrieve measurements.

**Key Methods:**

- :meth:`~sgu_client.client.levels.observed.ObservedGroundwaterLevelClient.get_stations` - Retrieve groundwater monitoring stations
- :meth:`~sgu_client.client.levels.observed.ObservedGroundwaterLevelClient.get_station_by_name` - Find a specific station by name
- :meth:`~sgu_client.client.levels.observed.ObservedGroundwaterLevelClient.get_stations_by_names` - Find multiple stations by names
- :meth:`~sgu_client.client.levels.observed.ObservedGroundwaterLevelClient.get_measurements_by_name` - Get measurements for a specific station
- :meth:`~sgu_client.client.levels.observed.ObservedGroundwaterLevelClient.get_measurements_by_names` - Get measurements for multiple stations

**Filtering Options:**

- **bbox**: Spatial filter (bounding box)
- **datetime**: Temporal filter (ISO 8601 datetime or interval)
- **filter**: CQL filter expression for advanced queries
- **limit**: Maximum number of results to return

.. automodule:: sgu_client.client.levels.observed
   :members:
   :undoc-members:
   :show-inheritance:

Data Models
~~~~~~~~~~~

.. automodule:: sgu_client.models.observed
   :members:
   :undoc-members:
   :show-inheritance:

Modeled Groundwater Levels
---------------------------

Client Interface
~~~~~~~~~~~~~~~~

The :class:`~sgu_client.client.levels.modeled.ModeledGroundwaterLevelClient` provides access to predicted groundwater levels from hydrological models.

**Key Methods:**

- :meth:`~sgu_client.client.levels.modeled.ModeledGroundwaterLevelClient.get_area`
- :meth:`~sgu_client.client.levels.modeled.ModeledGroundwaterLevelClient.get_areas`
- :meth:`~sgu_client.client.levels.modeled.ModeledGroundwaterLevelClient.get_levels_by_area`
- :meth:`~sgu_client.client.levels.modeled.ModeledGroundwaterLevelClient.get_levels_by_areas`
- :meth:`~sgu_client.client.levels.modeled.ModeledGroundwaterLevelClient.get_levels_by_coords`

.. automodule:: sgu_client.client.levels.modeled
   :members:
   :undoc-members:
   :show-inheritance:

Data Models
~~~~~~~~~~~

.. automodule:: sgu_client.models.modeled
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------

- :doc:`core` - Core client and configuration
- :doc:`models` - Base model infrastructure
- :doc:`utilities` - DataFrame conversion utilities
