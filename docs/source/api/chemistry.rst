Groundwater Chemistry API
==========================

The groundwater chemistry API provides access to water quality measurements from monitoring stations, including chemical composition, pH, conductivity, and other parameters.

Overview
--------

The chemistry API is accessed through ``client.chemistry`` and provides methods to query chemical measurements from groundwater monitoring stations.

Data comes from SGU's *Grundvattenkvalitet, analysresultat och provplatser (version 2)* OGC API, which has two collections:
sampling sites (``provplatser``) and analysis results (``analysresultat``).

**Quick Example:**

.. code-block:: python

   from sgu_client import SGUClient

   client = SGUClient()

   # Find a sampling site and its national site ID
   site = client.chemistry.get_sampling_site_by_name(site_id="TTK-442-M")
   national_site_id = site.properties.national_site_id

   # Get analysis results for the site (national_site_id is the fastest lookup)
   results = client.chemistry.get_results_by_site(
       national_site_id,
       tmin="2020-01-01",
       tmax="2024-01-01",
   )

   # Get all lead measurements since 2020
   lead = client.chemistry.get_results_by_parameter("Bly", tmin="2020-01-01")

   # Convert to pandas DataFrame for analysis
   df = results.to_dataframe()
   print(df[['sampling_date', 'parameter_name', 'measurement_value', 'unit']].head())

Chemistry Client
----------------

The :class:`~sgu_client.client.chemistry.chemistry.GroundwaterChemistryClient` provides methods to query groundwater chemistry data.

**Key Methods:**

- ``get_sampling_sites()`` / ``get_analysis_results()`` - Query the collections directly with OGC API filters
- ``get_sampling_site_by_name()`` / ``get_sampling_sites_by_names()`` - Find sites by ``site_id``, ``site_name`` or ``national_site_id``
- ``get_results_by_site()`` / ``get_results_by_sites()`` - Get analysis results for one or more sites
- ``get_results_by_parameter()`` - Get analysis results for a chemical parameter, optionally per site

**Identifying sites:**

Analysis results reference sampling sites only by national site ID (``nationellt_provplatsid``).
Passing ``national_site_id`` is therefore the recommended and fastest option; ``site_id``
(``platsbeteckning``) and ``site_name`` (``provplatsnamn``) trigger an additional request to
look up the site, and log a warning.

**Filtering Options:**

- **bbox**: Spatial filter (bounding box)
- **datetime**: Temporal filter (ISO 8601 datetime or interval)
- **filter_expr**: CQL filter expression, e.g. ``"parameternamn='Bly' AND provtagningsdatum>='2020-01-01'"``
- **limit**: Maximum number of results to return (paginated automatically)

**Common Parameters:**

Parameters are identified by SGU's Swedish parameter names (``parameter_name``), for example:

- ``pH``
- ``Konduktivitet`` (electrical conductivity)
- ``Klorid``, ``Svavelsulfat`` (major ions)
- ``Nitratkväve`` (nutrients)
- ``Bly`` (trace elements)

.. automodule:: sgu_client.client.chemistry.chemistry
   :members:
   :undoc-members:
   :show-inheritance:

Chemistry Data Models
---------------------

The chemistry data uses typed Pydantic models for sampling sites and analysis results.

.. automodule:: sgu_client.models.chemistry
   :members:
   :undoc-members:
   :show-inheritance:

See Also
--------

- :doc:`core` - Core client and configuration
- :doc:`models` - Base model infrastructure
- :doc:`utilities` - DataFrame conversion for chemistry analysis
