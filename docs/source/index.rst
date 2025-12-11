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

        In this example we fetch groundwater station data and measurements in just a few lines of Python code.

        .. code-block:: python

            # Import the SGU Client
            from sgu_client import SGUClient

            # Initialize the client
            client = SGUClient()

            # Get groundwater monitoring stations in southern Sweden
            stations = client.levels.observed.get_stations(
                bbox=[12.0, 55.0, 16.0, 58.0],
                limit=50
            )

            # Get recent measurements with date filtering
            measurements = client.levels.observed.get_measurements(
                datetime="2023-01-01/2024-01-01",
                limit=1000
            )

            # Convert to pandas DataFrame (requires pandas)
            df = measurements.to_dataframe()
            print(df[['observation_date', 'grundvattenniva_m_o_h']].head())

    .. tab-item:: Result

        .. figure:: _static/example_output.svg
            :width: 100%
            :align: center

            Example output showing groundwater measurements converted to a pandas DataFrame

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

Links
-----

* `GitHub Repository <https://github.com/officialankan/sgu-client>`_
* `PyPI Package <https://pypi.org/project/sgu-client/>`_
* `Issue Tracker <https://github.com/officialankan/sgu-client/issues>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
