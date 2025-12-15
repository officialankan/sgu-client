SGU Client Documentation
========================

A modern Python client library for accessing Geological Survey of Sweden (SGU) groundwater data APIs with type safety and pandas integration.

Installation
------------

Install using pip:

.. code-block:: bash

   pip install sgu-client

For pandas support:

.. code-block:: bash

   pip install "sgu-client[recommended]"

Quick Example
-------------

.. tab-set::

    .. tab-item:: Python

        .. code-block:: python

            # import the SGU Client
            from sgu_client import SGUClient

            # initialize the client
            client = SGUClient()

            # get groundwater monitoring stations in southern Sweden
            stations = client.levels.observed.get_stations(
                bbox=[12.0, 55.0, 16.0, 58.0],
                limit=50
            )

            # get recent measurements with date filtering
            measurements = client.levels.observed.get_measurements_by_name(
                "95_2",
                datetime="2024-10-01/2025-09-31",
            )

            # convert to pandas Series (requires pandas)
            s = measurements.to_series()
            s.plot()

    .. tab-item:: Result

        .. figure:: _static/lagga2.svg
            :width: 100%
            :align: center

Features
--------

- **Type-safe**: Full Pydantic validation for all API responses
- **Pandas integration**: Convert data to DataFrames with `to_dataframe()`
- **Comprehensive API coverage**: Observed/modeled groundwater levels, chemistry data
- **Error handling**: Robust exception handling with automatic retries
- **Modern Python**: Requires Python 3.11+

Documentation
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
   about
