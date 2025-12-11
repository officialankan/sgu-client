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

Quick Start
-----------

.. code-block:: python

   from sgu_client import SGUClient

   # Initialize the client
   client = SGUClient()

   # Get groundwater stations
   stations = client.levels.observed.get_stations(limit=10)

   # Get measurements
   measurements = client.levels.observed.get_measurements(limit=100)

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
