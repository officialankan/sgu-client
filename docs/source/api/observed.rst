Observed groundwater levels
===========================

.. currentmodule:: sgu_client.client.levels.observed

Measured groundwater levels from SGU's monitoring stations, available as
``client.levels.observed``. See :doc:`/user_guide/levels` for a walkthrough.

Methods
-------

.. autosummary::
   :nosignatures:

   ~ObservedGroundwaterLevelClient.get_stations
   ~ObservedGroundwaterLevelClient.get_station
   ~ObservedGroundwaterLevelClient.get_station_by_name
   ~ObservedGroundwaterLevelClient.get_stations_by_names
   ~ObservedGroundwaterLevelClient.get_measurements
   ~ObservedGroundwaterLevelClient.get_measurement
   ~ObservedGroundwaterLevelClient.get_measurements_by_name
   ~ObservedGroundwaterLevelClient.get_measurements_by_names

.. currentmodule:: sgu_client.models.observed

Models
------

.. autosummary::
   :nosignatures:

   GroundwaterStationCollection
   GroundwaterStation
   GroundwaterStationProperties
   GroundwaterMeasurementCollection
   GroundwaterMeasurement
   GroundwaterMeasurementProperties

Client
------

.. autoclass:: sgu_client.client.levels.observed.ObservedGroundwaterLevelClient

Model details
-------------

.. automodule:: sgu_client.models.observed
