"""Pydantic models for groundwater chemistry data from SGU API."""

from typing import TYPE_CHECKING, Any

from pydantic import Field, field_validator

from sgu_client.models.base import SGUBaseModel
from sgu_client.models.dates import ApiDatetime
from sgu_client.models.features import Feature, FeatureCollection, TimeSeriesCollection
from sgu_client.utils.pandas_helpers import get_pandas, optional_pandas_method

if TYPE_CHECKING:
    import pandas as pd


def _normalize_county_code(value: Any) -> str | None:
    """Normalize county codes to two-digit strings.

    The v2 API returns `lanskod` as a string ("04") for sampling sites but as an
    integer (4) for analysis results.
    """
    if value is None:
        return None
    return str(value).zfill(2)


# Sampling site properties (English field names with Swedish API aliases)
class SamplingSiteProperties(SGUBaseModel):
    """Properties for a groundwater chemistry sampling site."""

    # Site identification
    object_id: int | None = Field(None, alias="objectid", description="Object ID")
    national_site_id: int | None = Field(
        None, alias="nationellt_provplatsid", description="National sampling site ID"
    )
    site_uuid: str | None = Field(
        None, alias="provplatsuuid", description="Sampling site UUID"
    )
    monitoring_station_id: int | None = Field(
        None, alias="overvakningsstation", description="Monitoring station ID"
    )
    station_id: str | None = Field(
        None, alias="platsbeteckning", description="Station identifier"
    )
    site_name: str | None = Field(
        None, alias="provplatsnamn", description="Sampling site name"
    )
    other_designations: str | None = Field(
        None, alias="andra_beteckningar", description="Other site designations"
    )
    eu_station_code: str | None = Field(
        None, alias="eu_cd", description="EU station code"
    )
    eu_groundwater_body: str | None = Field(
        None, alias="eucd_gwb", description="EU groundwater body"
    )

    # Site classification
    site_type_code: str | None = Field(
        None, alias="provplatstyp", description="Sampling site type code"
    )
    site_type_description: str | None = Field(
        None, alias="provplatstyp_tx", description="Sampling site type description"
    )
    site_category_code: str | None = Field(
        None,
        alias="provplatskat_bedgr",
        description="Sampling site category code (assessment basis)",
    )
    site_category_description: str | None = Field(
        None,
        alias="provplatskat_bedgr_tx",
        description="Sampling site category description",
    )

    # Coordinates (projected, SWEREF 99 TM)
    coordinates_hidden: str | None = Field(
        None, alias="dold_koordinat", description="Whether coordinates are hidden"
    )
    north_coordinate: float | None = Field(
        None, alias="n", description="North coordinate"
    )
    east_coordinate: float | None = Field(
        None, alias="e", description="East coordinate"
    )

    # Position metadata
    positioning_method_code: str | None = Field(
        None, alias="positioneringsmetod", description="Positioning method code"
    )
    positioning_method_description: str | None = Field(
        None,
        alias="positioneringsmetod_tx",
        description="Positioning method description",
    )
    position_quality_code: str | None = Field(
        None, alias="positionskvalitet", description="Position quality code"
    )
    position_quality_description: str | None = Field(
        None, alias="positionskvalitet_tx", description="Position quality description"
    )

    # Administrative location
    county_code: str | None = Field(None, alias="lanskod", description="County code")
    county: str | None = Field(None, alias="lan", description="County")
    municipality_code: str | None = Field(
        None, alias="kommunkod", description="Municipality code"
    )
    municipality: str | None = Field(None, alias="kommun", description="Municipality")
    region_code: str | None = Field(
        None, alias="region_bdgr", description="Region code (assessment basis)"
    )
    region_description: str | None = Field(
        None, alias="region_bdgr_tx", description="Region description"
    )

    # Hydrological location
    water_district_code: str | None = Field(
        None, alias="vattendistrikt", description="Water district code"
    )
    water_district_description: str | None = Field(
        None, alias="vattendistrikt_tx", description="Water district description"
    )
    sub_catchment_name: str | None = Field(
        None, alias="delaro_namn", description="Sub-catchment name"
    )
    sub_catchment_code: str | None = Field(
        None, alias="delaro_ms_cd", description="Sub-catchment MS code"
    )
    sub_catchment_uuid: str | None = Field(
        None, alias="delaro_uuid", description="Sub-catchment UUID"
    )
    water_body_catchment_id: str | None = Field(
        None, alias="vattenforekomst_aro_id", description="Water body catchment ID"
    )
    main_catchment_id: int | None = Field(
        None, alias="huvudavrinningsomrade_id", description="Main catchment area ID"
    )

    # Well/site characteristics
    reference_level: float | None = Field(
        None, alias="refniva", description="Reference level"
    )
    elevation_system: str | None = Field(
        None, alias="hojdsystem", description="Elevation reference system"
    )
    elevation_system_description: str | None = Field(
        None,
        alias="hojdsystem_tx",
        description="Elevation reference system description",
    )
    elevation_method_code: str | None = Field(
        None, alias="hojdmetod", description="Elevation method code"
    )
    elevation_method_description: str | None = Field(
        None, alias="hojdmetod_tx", description="Elevation method description"
    )
    pipe_height: float | None = Field(
        None, alias="rorhojd", description="Pipe height above ground"
    )
    pipe_length: float | None = Field(None, alias="rorlangd", description="Pipe length")
    borehole_inclination: float | None = Field(
        None, alias="borrhalslutning", description="Borehole inclination"
    )
    screen_length: float | None = Field(
        None, alias="sillangd", description="Well screen length"
    )
    inner_diameter: float | None = Field(
        None, alias="innerdiam", description="Inner diameter"
    )
    material_code: str | None = Field(
        None, alias="material", description="Well material code"
    )
    material_description: str | None = Field(
        None, alias="material_tx", description="Well material description"
    )

    # Soil
    soil_depth_qualifier: str | None = Field(
        None, alias="tecken_jorddjup", description="Soil depth sign/qualifier"
    )
    soil_depth: float | None = Field(None, alias="jorddjup", description="Soil depth")
    soil_type_code: str | None = Field(
        None, alias="jordart", description="Soil type code"
    )
    soil_type_description: str | None = Field(
        None, alias="jordart_tx", description="Soil type description"
    )
    overlying_soil_code: str | None = Field(
        None, alias="jord_ovan_jord", description="Overlying soil type code"
    )
    overlying_soil_description: str | None = Field(
        None, alias="jord_ovan_jord_tx", description="Overlying soil type description"
    )
    soil_genesis_code: str | None = Field(
        None, alias="genes_jord", description="Soil genesis code"
    )
    soil_genesis_description: str | None = Field(
        None, alias="genes_jord_tx", description="Soil genesis description"
    )

    # Bedrock and aquifer
    rock_type_code: str | None = Field(
        None, alias="bergart", description="Rock type code"
    )
    rock_type_description: str | None = Field(
        None, alias="bergart_tx", description="Rock type description"
    )
    aquifer_code: str | None = Field(None, alias="akvifer", description="Aquifer code")
    aquifer_description: str | None = Field(
        None, alias="akvifer_tx", description="Aquifer description"
    )
    groundwater_environment_code: str | None = Field(
        None,
        alias="gvmiljo_bedgr",
        description="Groundwater environment code (assessment basis)",
    )
    groundwater_environment_description: str | None = Field(
        None,
        alias="gvmiljo_bedgr_tx",
        description="Groundwater environment description",
    )
    geohydrological_position_code: str | None = Field(
        None, alias="geohylag", description="Geohydrological position code"
    )
    geohydrological_position_description: str | None = Field(
        None, alias="geohylag_tx", description="Geohydrological position description"
    )

    # Sampling history
    established_date: ApiDatetime = Field(
        None, alias="etabldatum", description="Site establishment date (midnight UTC)"
    )
    first_sample_date: ApiDatetime = Field(
        None, alias="forstaprov", description="Date of first sample (midnight UTC)"
    )
    latest_sample_date: ApiDatetime = Field(
        None, alias="senasteprov", description="Date of latest sample (midnight UTC)"
    )
    sample_count: int | None = Field(
        None, alias="antal_prov", description="Number of samples collected"
    )
    sampling_occasion_count: int | None = Field(
        None, alias="antal_provtillf", description="Number of sampling occasions"
    )
    sample_types: str | None = Field(
        None, alias="provtyper", description="Sample types collected"
    )
    media: str | None = Field(None, alias="media", description="Sampled media")
    sampling_purpose_code: str | None = Field(
        None, alias="provtagningssyfte", description="Sampling purpose code"
    )
    sampling_purpose_description: str | None = Field(
        None, alias="provtagningssyften_tx", description="Sampling purpose description"
    )

    # Monitoring program flags
    national_monitoring: str | None = Field(
        None, alias="nationell", description="National monitoring program (ja/nej)"
    )
    regional_monitoring: str | None = Field(
        None, alias="regional", description="Regional monitoring program (ja/nej)"
    )

    # Classification and symbols
    symbol: str | None = Field(
        None, alias="symbol", description="Symbol/classification marker"
    )

    # Analysis result links
    analyses_csv_url: str | None = Field(
        None,
        alias="analysdata_csv",
        description="URL to CSV file with analysis results",
    )
    analyses_json_url: str | None = Field(
        None,
        alias="analysdata_json",
        description="URL to JSON file with analysis results",
    )

    _county_code = field_validator("county_code", mode="before")(_normalize_county_code)


class SamplingSite(Feature[SamplingSiteProperties]):
    """A groundwater chemistry sampling site (GeoJSON Feature)."""


# Analysis result properties (English field names with Swedish API aliases)
class AnalysisResultProperties(SGUBaseModel):
    """Properties for a groundwater chemistry analysis result."""

    # Result identification
    object_id: int | None = Field(None, alias="objectid", description="Object ID")
    result_id: int | None = Field(None, alias="resultatid", description="Result ID")
    delivery_id: str | None = Field(None, alias="leveransid", description="Delivery ID")
    origin: str | None = Field(None, alias="ursprung", description="Data origin")

    # Commissioning and reporting
    commissioned_by_code: str | None = Field(
        None, alias="bestallare", description="Commissioning organisation code"
    )
    commissioned_by_description: str | None = Field(
        None, alias="bestallare_tx", description="Commissioning organisation"
    )
    survey_type: str | None = Field(
        None, alias="undersokningstyp", description="Survey type"
    )
    commissioned_survey: str | None = Field(
        None, alias="bestalld_undersokning", description="Commissioned survey"
    )
    performing_organisation: str | None = Field(
        None, alias="utfor_org", description="Performing organisation"
    )
    performing_organisation_type: str | None = Field(
        None, alias="utfor_org_typ", description="Performing organisation type"
    )
    report_name: str | None = Field(
        None, alias="rapportnamn", description="Report name"
    )
    report_name_diva: str | None = Field(
        None, alias="rapportnamn_diva", description="Report name in DiVA"
    )
    diva_url: str | None = Field(None, alias="diva_url", description="DiVA report URL")

    # Site identification
    national_site_id: int | None = Field(
        None, alias="nationellt_provplatsid", description="National sampling site ID"
    )
    monitoring_station_id: int | None = Field(
        None, alias="overvakningsstation", description="Monitoring station ID"
    )
    site_uuid: str | None = Field(
        None, alias="provplatsuuid", description="Sampling site UUID"
    )
    site_name: str | None = Field(
        None, alias="provplatsnamn", description="Sampling site name"
    )
    site_type_code: str | None = Field(
        None, alias="provplatstyp", description="Sampling site type code"
    )

    # Location
    county_code: str | None = Field(None, alias="lanskod", description="County code")
    county: str | None = Field(None, alias="lan", description="County")
    municipality_code: str | None = Field(
        None, alias="kommunkod", description="Municipality code"
    )
    municipality: str | None = Field(None, alias="kommun", description="Municipality")
    east_coordinate: float | None = Field(
        None, alias="e", description="East coordinate"
    )
    north_coordinate: float | None = Field(
        None, alias="n", description="North coordinate"
    )
    actual_sampling_point_east: float | None = Field(
        None,
        alias="fkt_provpunkt_e",
        description="Actual sampling point east coordinate",
    )
    actual_sampling_point_north: float | None = Field(
        None,
        alias="fkt_provpunkt_n",
        description="Actual sampling point north coordinate",
    )

    # Sampling
    sampling_organisation_code: str | None = Field(
        None, alias="provtag_org", description="Sampling organisation code"
    )
    sampling_organisation_description: str | None = Field(
        None, alias="provtag_org_tx", description="Sampling organisation"
    )
    sampling_date: ApiDatetime = Field(
        None, alias="provtagningsdatum", description="Sampling date (UTC)"
    )
    sampling_end_date: ApiDatetime = Field(
        None, alias="provtagning_slutdatum", description="Sampling end date (UTC)"
    )
    sampling_purpose_code: str | None = Field(
        None, alias="provtagningssyfte", description="Sampling purpose code"
    )
    sampling_purpose_description: str | None = Field(
        None, alias="provtagningssyfte_tx", description="Sampling purpose description"
    )
    sampling_method: str | None = Field(
        None, alias="provtagningsmetod", description="Sampling method"
    )
    sampling_method_url: str | None = Field(
        None, alias="provtagningsmetod_url", description="Sampling method URL"
    )
    sample_data_type: str | None = Field(
        None, alias="provdatatyp", description="Sample data type"
    )
    site_environment: str | None = Field(
        None, alias="provplatsmiljo", description="Sampling site environment"
    )
    media: str | None = Field(None, alias="media", description="Sampled media")
    accredited_sampler: str | None = Field(
        None, alias="ackrediteradprovtagare", description="Accredited sampler"
    )
    direct_treatment: str | None = Field(
        None, alias="direktbehandling", description="Direct sample treatment"
    )
    direct_treatment_url: str | None = Field(
        None, alias="direktbehandling_url", description="Direct sample treatment URL"
    )
    filtered: str | None = Field(
        None, alias="filtrerat", description="Whether the sample was filtered"
    )
    filter_size: str | None = Field(
        None, alias="filterstorlek", description="Filter size"
    )
    purge_time: str | None = Field(
        None, alias="omsattningstid", description="Well purge time"
    )
    purge_volume: str | None = Field(
        None, alias="omsattningsvolym", description="Well purge volume"
    )
    purge_to_sample_time: str | None = Field(
        None, alias="omsatt_tid_till_prov", description="Time from purge to sampling"
    )
    sample_comment: str | None = Field(
        None, alias="kommentar_prov", description="Sample comment"
    )
    original_sample_code: str | None = Field(
        None, alias="provkodoriginal", description="Original sample code"
    )

    # Laboratory
    laboratory: str | None = Field(
        None, alias="laboratorium", description="Laboratory name"
    )
    laboratory_description: str | None = Field(
        None, alias="laboratorium_tx", description="Laboratory description"
    )
    performing_lab_id: str | None = Field(
        None, alias="utforarlabbid", description="Performing laboratory ID"
    )
    performing_lab_description: str | None = Field(
        None, alias="utforarlabbid_tx", description="Performing laboratory description"
    )
    lab_report_code: str | None = Field(
        None, alias="rapportkodlabb", description="Laboratory report code"
    )
    registration_date: ApiDatetime = Field(
        None, alias="registreringsdatum", description="Registration date (UTC)"
    )
    analysis_date: ApiDatetime = Field(
        None, alias="analysdatum", description="Analysis date (UTC)"
    )
    sample_preparation: str | None = Field(
        None, alias="provberedning", description="Sample preparation method"
    )
    sample_preparation_url: str | None = Field(
        None, alias="provberedning_url", description="Sample preparation method URL"
    )
    sample_container_code: str | None = Field(
        None, alias="provkarl", description="Sample container code"
    )
    sample_container_description: str | None = Field(
        None, alias="provkarl_tx", description="Sample container description"
    )
    sample_storage_code: str | None = Field(
        None, alias="provlagring", description="Sample storage code"
    )
    sample_storage_description: str | None = Field(
        None, alias="provlagring_tx", description="Sample storage description"
    )

    # Parameter (chemical substance measured)
    parameter_id: str | None = Field(
        None, alias="ntlkemiparameterid", description="National chemistry parameter ID"
    )
    parameter_name: str | None = Field(
        None, alias="parameternamn", description="Parameter/chemical substance name"
    )
    parameter_comment: str | None = Field(
        None, alias="parameter_anm", description="Parameter comment"
    )
    parameter_group: str | None = Field(
        None, alias="parametergrupp", description="Parameter group"
    )
    cas_number: str | None = Field(
        None, alias="cas_kod", description="CAS registry number"
    )

    # Measurement value
    measurement_value_text: str | None = Field(
        None, alias="matvardetext", description="Measurement value as text"
    )
    measurement_value: float | None = Field(
        None, alias="matvardetal", description="Measurement value (numeric)"
    )
    measurement_value_annotation: str | None = Field(
        None,
        alias="matvardetal_anm",
        description="Measurement value annotation/qualifier",
    )
    measurement_value_span: str | None = Field(
        None, alias="matvardespar", description="Measurement value span/range"
    )
    unit: str | None = Field(None, alias="enhet", description="Unit of measurement")
    unit_description: str | None = Field(
        None, alias="enhet_tx", description="Unit of measurement description"
    )
    measurement_standard_code: str | None = Field(
        None, alias="matvstd", description="Measurement standard code"
    )
    measurement_standard_description: str | None = Field(
        None, alias="matvstd_tx", description="Measurement standard description"
    )
    quantification_limit: str | None = Field(
        None, alias="loq", description="Limit of quantification (LOQ)"
    )
    detection_limit: str | None = Field(
        None, alias="lod", description="Limit of detection (LOD)"
    )
    measurement_uncertainty: str | None = Field(
        None, alias="matosakerhet", description="Measurement uncertainty"
    )
    measurement_uncertainty_unit_code: str | None = Field(
        None, alias="matosakerhetenhet", description="Measurement uncertainty unit code"
    )
    measurement_uncertainty_unit_description: str | None = Field(
        None, alias="matosakerhetenhet_tx", description="Measurement uncertainty unit"
    )
    measurement_uncertainty_type_code: str | None = Field(
        None, alias="matosakerhettyp", description="Measurement uncertainty type code"
    )
    measurement_uncertainty_type_description: str | None = Field(
        None, alias="matosakerhettyp_tx", description="Measurement uncertainty type"
    )
    measurement_comment: str | None = Field(
        None, alias="kommentar_matvarde", description="Measurement value comment"
    )

    # Analysis method
    method: str | None = Field(
        None, alias="analysmetod", description="Analysis method used"
    )
    method_url: str | None = Field(
        None, alias="analysmetod_url", description="Analysis method URL"
    )
    accredited_method: str | None = Field(
        None, alias="ackrediteradmetod", description="Accredited analysis method"
    )
    analysis_instrument: str | None = Field(
        None, alias="analysinstrument", description="Analysis instrument"
    )
    analysis_instrument_url: str | None = Field(
        None, alias="analysinstrument_url", description="Analysis instrument URL"
    )

    # Water type and quality control
    water_type_code: str | None = Field(
        None, alias="vattentyp", description="Water type code"
    )
    water_type_description: str | None = Field(
        None, alias="vattentyp_tx", description="Water type description"
    )
    quality_flag: str | None = Field(
        None, alias="kvalitetsflagga", description="Quality flag"
    )
    review_comment: str | None = Field(
        None, alias="granskningskommentar", description="Review comment"
    )

    _county_code = field_validator("county_code", mode="before")(_normalize_county_code)


class AnalysisResult(Feature[AnalysisResultProperties]):
    """A groundwater chemistry analysis result (GeoJSON Feature)."""


# Collection response models
class SamplingSiteCollection(FeatureCollection[SamplingSite]):
    """Collection of groundwater chemistry sampling sites (GeoJSON FeatureCollection).

    Its DataFrame has ``longitude`` and ``latitude`` columns, null for sites without
    a geometry.

    Examples:

        >>> from sgu_client import SGUClient
        >>> with SGUClient() as client:
        ...     sites = client.chemistry.get_sampling_sites(limit=10)
        ...     df = sites.to_dataframe()
        ...     print(df[['national_site_id', 'station_id', 'site_name']].head())
    """

    _geometry = "point"


class AnalysisResultCollection(TimeSeriesCollection[AnalysisResult]):
    """Collection of groundwater chemistry analysis results (GeoJSON FeatureCollection).

    Its DataFrame has no geometry columns. Sorted by ``sampling_date``;
    ``to_series()`` defaults to ``measurement_value``. ``pivot_by_parameter()``
    gives one column per chemical parameter.

    Examples:

        >>> from sgu_client import SGUClient
        >>> with SGUClient() as client:
        ...     results = client.chemistry.get_results_by_site(359366, limit=100)
        ...     df = results.to_dataframe()
        ...     print(df[['sampling_date', 'parameter_name', 'measurement_value']])
    """

    _date_column = "sampling_date"
    _series_column = "measurement_value"

    @optional_pandas_method("pivot_by_parameter() method")
    def pivot_by_parameter(
        self,
        values: str = "measurement_value",
        index: str = "sampling_date",
        columns: str = "parameter_name",
        aggfunc: str = "mean",
    ) -> "pd.DataFrame":
        """Pivot analysis results by parameter for easier time series analysis.

        This creates a wide-format DataFrame where each chemical parameter becomes
        a column, making it easy to analyze multiple parameters over time.

        Args:
            values: Column to use for values (default: 'measurement_value')
            index: Column to use as index (default: 'sampling_date')
            columns: Column to pivot into columns (default: 'parameter_name')
            aggfunc: Aggregation function if there are duplicate index/column pairs
                    (default: 'mean'). Can be 'mean', 'median', 'first', 'last', etc.

        Returns:
            Pivoted DataFrame with parameters as columns.

        Example:

            >>> from sgu_client import SGUClient
            >>> with SGUClient() as client:
            ...     results = client.chemistry.get_results_by_site(359366)
            ...     df_pivot = results.pivot_by_parameter()
            ...     # now df_pivot has columns like 'pH', 'Nitratkväve', 'Klorid', etc.
        """
        df = self.to_dataframe(sort_by_date=True)
        pd = get_pandas()

        if df.empty:
            return pd.DataFrame()

        # Validate columns exist
        for col in [values, index, columns]:
            if col not in df.columns:
                raise ValueError(f"Column '{col}' not found in DataFrame.")

        # Create pivot table
        pivot_df = df.pivot_table(
            values=values, index=index, columns=columns, aggfunc=aggfunc
        )

        return pivot_df
