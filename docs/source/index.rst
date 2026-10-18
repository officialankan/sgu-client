sgu-client
==========

A modern Python client for the groundwater data APIs of the Geological Survey of Sweden
(SGU), with typed responses and pandas integration.

Installation
------------

.. code-block:: bash

   uv add sgu-client
   # or: pip install sgu-client

For pandas support:

.. code-block:: bash

   uv add "sgu-client[recommended]"
   # or: pip install "sgu-client[recommended]"

Quick example
-------------

.. tab-set::
    :class: quick-example

    .. tab-item:: Python

        .. code-block:: python

            # import the SGU Client
            from sgu_client import SGUClient

            # create the client, which closes its session when the block ends
            with SGUClient() as client:

                # get groundwater monitoring stations in southern Sweden
                stations = client.levels.observed.get_stations(
                    bbox=[12.0, 55.0, 16.0, 58.0],
                    limit=50
                )

                # get recent measurements with date filtering
                measurements = client.levels.observed.get_measurements_by_name(
                    "95_2",
                    tmin="2024-10-01",
                    tmax="2025-09-30",
                )

            # convert to pandas Series (requires pandas)
            s = measurements.to_series()
            s.plot()

    .. tab-item:: Result

        .. image:: _static/lagga2.svg
            :alt: Plot of groundwater levels at station 95_2
            :align: center

Explore the docs
----------------

.. grid:: 1 1 3 3
   :gutter: 3

   .. grid-item-card:: :octicon:`book;1.5em;sd-mr-1` User Guide
      :link: user_guide/index
      :link-type: doc
      :text-align: center

      Install, create a client and fetch groundwater levels and chemistry data.

   .. grid-item-card:: :octicon:`code;1.5em;sd-mr-1` API Reference
      :link: api
      :link-type: doc
      :text-align: center

      Every client method, response model and field, with its SGU API name.

   .. grid-item-card:: :octicon:`info;1.5em;sd-mr-1` About
      :link: about/index
      :link-type: doc
      :text-align: center

      License, data source and changelog.

.. toctree::
   :hidden:

   user_guide/index
   api
   about/index
