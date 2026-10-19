Groundwater chemistry
=====================

.. currentmodule:: sgu_client.client.chemistry.chemistry

Water quality analyses from SGU's *Grundvattenkvalitet, analysresultat och provplatser
(version 2)* API, available as ``client.chemistry``. See :doc:`/user_guide/chemistry`
for a walkthrough.

Methods
-------

.. autosummary::
   :nosignatures:

   ~GroundwaterChemistryClient.get_sampling_sites
   ~GroundwaterChemistryClient.get_sampling_site
   ~GroundwaterChemistryClient.get_sampling_site_by_name
   ~GroundwaterChemistryClient.get_sampling_sites_by_names
   ~GroundwaterChemistryClient.get_analysis_results
   ~GroundwaterChemistryClient.get_analysis_result
   ~GroundwaterChemistryClient.get_results_by_site
   ~GroundwaterChemistryClient.get_results_by_sites
   ~GroundwaterChemistryClient.get_results_by_parameter

.. currentmodule:: sgu_client.models.chemistry

Models
------

.. autosummary::
   :nosignatures:

   SamplingSiteCollection
   SamplingSite
   SamplingSiteProperties
   AnalysisResultCollection
   AnalysisResult
   AnalysisResultProperties

Client
------

.. autoclass:: sgu_client.client.chemistry.chemistry.GroundwaterChemistryClient

Model details
-------------

.. automodule:: sgu_client.models.chemistry
