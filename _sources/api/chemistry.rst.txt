Groundwater Chemistry API
==========================

The groundwater chemistry API provides access to water quality measurements from monitoring stations, including chemical composition, pH, conductivity, and other parameters.

Overview
--------

The chemistry API is accessed through ``client.chemistry`` and provides methods to query chemical measurements from groundwater monitoring stations.

**Quick Example:**

.. code-block:: python

   from sgu_client import SGUClient

   client = SGUClient()

   # Get chemistry measurements
   measurements = client.chemistry.get_measurements(
       bbox=[12.0, 55.0, 16.0, 58.0],
       datetime="2023-01-01/2024-01-01",
       limit=100
   )

   # Get stations with chemistry data
   stations = client.chemistry.get_stations(limit=50)

   # Convert to pandas DataFrame for analysis
   df = measurements.to_dataframe()
   print(df[['observation_date', 'parameter', 'value', 'unit']].head())

Chemistry Client
----------------

The :class:`~sgu_client.client.chemistry.chemistry.GroundwaterChemistryClient` provides methods to query groundwater chemistry data.

**Key Methods:**

- ``get_measurements()`` - Retrieve chemistry measurements
- ``get_stations()`` - Retrieve stations with chemistry data
- ``get_measurement_by_name()`` - Find measurements for a specific station

**Filtering Options:**

- **bbox**: Spatial filter (bounding box)
- **datetime**: Temporal filter (ISO 8601 datetime or interval)
- **filter**: CQL filter expression for parameter-specific queries
- **limit**: Maximum number of results to return

**Common Parameters:**

The chemistry API tracks various water quality parameters including:

- pH levels
- Electrical conductivity
- Major ions (Ca, Mg, Na, K, Cl, SO4, HCO3)
- Nutrients (NO3, NH4, PO4)
- Trace elements
- Dissolved gases

.. automodule:: sgu_client.client.chemistry.chemistry
   :members:
   :undoc-members:
   :show-inheritance:

Chemistry Data Models
---------------------

The chemistry data uses typed Pydantic models for measurements and station metadata.

.. automodule:: sgu_client.models.chemistry
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------

- :doc:`core` - Core client and configuration
- :doc:`models` - Base model infrastructure
- :doc:`utilities` - DataFrame conversion for chemistry analysis
