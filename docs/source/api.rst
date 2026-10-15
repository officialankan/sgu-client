API Reference
=============

The reference is organized the way you reach things from :class:`~sgu_client.SGUClient`.
For narrative introductions and examples, see the :doc:`user_guide/index`.

.. grid:: 1 2 2 2
   :gutter: 3

   .. grid-item-card:: Client
      :link: api/client
      :link-type: doc

      ``SGUClient`` and ``client.levels``, the entry points to every endpoint.

   .. grid-item-card:: Configuration & exceptions
      :link: api/config
      :link-type: doc

      ``SGUConfig`` options and the exception hierarchy.

   .. grid-item-card:: Observed groundwater levels
      :link: api/observed
      :link-type: doc

      ``client.levels.observed``: monitoring stations and measurements.

   .. grid-item-card:: Modeled groundwater levels
      :link: api/modeled
      :link-type: doc

      ``client.levels.modeled``: SGU-HYPE model areas and levels.

   .. grid-item-card:: Groundwater chemistry
      :link: api/chemistry
      :link-type: doc

      ``client.chemistry``: sampling sites and analysis results.

   .. grid-item-card:: Shared models
      :link: api/models
      :link-type: doc

      Base response classes and GeoJSON geometry types.

.. toctree::
   :hidden:

   api/client
   api/config
   api/observed
   api/modeled
   api/chemistry
   api/models
   api/internals
