"""Mock response fixtures for SGU API tests.

These fixtures provide realistic API response data for testing without making
actual HTTP requests. They're based on real SGU API responses to ensure
compatibility.
"""

from datetime import UTC, datetime
from typing import Any


def create_mock_station_feature(
    station_id: str = "stationer.4086",
    platsbeteckning: str = "95_2",
    obsplatsnamn: str = "Lagga_2",
    coordinates: list[float] | None = None,
) -> dict[str, Any]:
    """Create a single mock groundwater station feature."""
    if coordinates is None:
        coordinates = [16.123456, 58.789012]

    return {
        "type": "Feature",
        "id": station_id,
        "geometry": {"type": "Point", "coordinates": coordinates},
        "properties": {
            "rowid": 12345,
            "platsbeteckning": platsbeteckning,
            "obsplatsnamn": obsplatsnamn,
            "kommun": "Kalmar",
            "lan": "Kalmar län",
            "landskap": "Småland",
            "akvifer_tx": "Berg",
            "djup_m": 15.5,
            "roropp_m_o_h": 89.2,
            "rorbotten_m_o_h": 73.7,
            "markyta_m_o_h": 87.8,
            "status": "aktiv",
            "installerad": "1985-03-15",
            "avslutad": None,
            "operator": "SGU",
            "beskrivning": "Observationsrör för grundvattennivå",
        },
        "links": [
            {
                "href": f"https://resource.sgu.se/service/sgustationen/collections/stationer/items/{station_id}",
                "rel": "self",
                "type": "application/geo+json",
                "title": "This document",
            }
        ],
    }


def create_mock_measurement_feature(
    measurement_id: str = "nivaer.1",
    platsbeteckning: str = "95_2",
    observation_date: datetime | None = None,
    water_level: float = 2.45,
    metod: str = "klucklod",
) -> dict[str, Any]:
    """Create a single mock groundwater measurement feature."""
    if observation_date is None:
        observation_date = datetime(2023, 6, 15, 10, 30, 0, tzinfo=UTC)

    return {
        "type": "Feature",
        "id": measurement_id,
        "geometry": {"type": "Point", "coordinates": [16.123456, 58.789012]},
        "properties": {
            "rowid": 12345,  # Required field
            "platsbeteckning": platsbeteckning,
            "obsdatum": observation_date.isoformat(),
            "grundvattenniva_m_o_h": water_level,
            "grundvattenniva_m_urok": 85.35,  # markyta_m_o_h - grundvattenniva_m_o_h
            "metod_for_matning": metod,
            "matutrustning": "Klucklod",
            "osäkerhet_m": 0.01,
            "kommentar": None,
            "status": "godkänd",
        },
        "links": [
            {
                "href": f"https://resource.sgu.se/service/sgustationen/collections/nivaer/items/{measurement_id}",
                "rel": "self",
                "type": "application/geo+json",
                "title": "This document",
            }
        ],
    }


def create_mock_station_collection_response(
    stations: list[dict[str, Any]] | None = None,
    number_returned: int | None = None,
    number_matched: int | None = None,
) -> dict[str, Any]:
    """Create a mock GroundwaterStationCollection response."""
    if stations is None:
        stations = [create_mock_station_feature()]

    if number_returned is None:
        number_returned = len(stations)

    if number_matched is None:
        number_matched = number_returned

    return {
        "type": "FeatureCollection",
        "features": stations,
        "numberReturned": number_returned,
        "numberMatched": number_matched,
        "timeStamp": "2024-09-21T10:30:00Z",
        "links": [
            {
                "href": "https://resource.sgu.se/service/sgustationen/collections/stationer/items",
                "rel": "self",
                "type": "application/geo+json",
                "title": "This document",
            }
        ],
    }


def create_mock_measurement_collection_response(
    measurements: list[dict[str, Any]] | None = None,
    number_returned: int | None = None,
    number_matched: int | None = None,
) -> dict[str, Any]:
    """Create a mock GroundwaterMeasurementCollection response."""
    if measurements is None:
        measurements = [create_mock_measurement_feature()]

    if number_returned is None:
        number_returned = len(measurements)

    if number_matched is None:
        number_matched = number_returned

    return {
        "type": "FeatureCollection",
        "features": measurements,
        "numberReturned": number_returned,
        "numberMatched": number_matched,
        "timeStamp": "2024-09-21T10:30:00Z",
        "links": [
            {
                "href": "https://resource.sgu.se/service/sgustationen/collections/nivaer/items",
                "rel": "self",
                "type": "application/geo+json",
                "title": "This document",
            }
        ],
    }


def create_mock_single_station_response(
    station_id: str = "stationer.4086",
    platsbeteckning: str = "95_2",
    obsplatsnamn: str = "Lagga_2",
) -> dict[str, Any]:
    """Create a mock response for getting a single station by ID."""
    station = create_mock_station_feature(
        station_id=station_id,
        platsbeteckning=platsbeteckning,
        obsplatsnamn=obsplatsnamn,
    )
    return create_mock_station_collection_response([station])


def create_mock_single_measurement_response(
    measurement_id: str = "nivaer.1",
    platsbeteckning: str = "95_2",
    metod: str = "klucklod",
) -> dict[str, Any]:
    """Create a mock response for getting a single measurement by ID."""
    measurement = create_mock_measurement_feature(
        measurement_id=measurement_id, platsbeteckning=platsbeteckning, metod=metod
    )
    return create_mock_measurement_collection_response([measurement])


def create_mock_multiple_stations_response(
    platsbeteckningar: list[str] | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Create a mock response for multiple stations."""
    if platsbeteckningar is None:
        platsbeteckningar = ["95_2", "101_1"]

    stations = []
    for i, platsbeteckning in enumerate(platsbeteckningar):
        station = create_mock_station_feature(
            station_id=f"stationer.{4086 + i}",
            platsbeteckning=platsbeteckning,
            obsplatsnamn=f"Station_{platsbeteckning}",
            coordinates=[16.123456 + i * 0.1, 58.789012 + i * 0.1],
        )
        stations.append(station)

    return create_mock_station_collection_response(
        stations=stations[:limit],
        number_returned=min(len(stations), limit),
        number_matched=len(stations),
    )


def create_mock_multiple_measurements_response(
    platsbeteckning: str = "95_2",
    count: int = 5,
    start_date: datetime | None = None,
) -> dict[str, Any]:
    """Create a mock response for multiple measurements."""
    if start_date is None:
        start_date = datetime(2023, 1, 1, tzinfo=UTC)

    measurements = []
    for i in range(count):
        measurement_date = start_date.replace(day=1 + i * 7)  # Weekly measurements
        measurement = create_mock_measurement_feature(
            measurement_id=f"nivaer.{i + 1}",
            platsbeteckning=platsbeteckning,
            observation_date=measurement_date,
            water_level=2.45 + i * 0.1,  # Varying water levels
        )
        measurements.append(measurement)

    return create_mock_measurement_collection_response(
        measurements=measurements, number_returned=count, number_matched=count
    )


def create_mock_empty_collection_response() -> dict[str, Any]:
    """Create a mock response for an empty collection."""
    return create_mock_station_collection_response(
        stations=[], number_returned=0, number_matched=0
    )


def create_mock_error_response(
    status_code: int = 500, message: str = "Internal Server Error"
) -> dict[str, Any]:
    """Create a mock error response."""
    return {
        "error": message,
        "status": status_code,
        "timestamp": "2024-09-21T10:30:00Z",
    }


# Modeled groundwater mock responses


def create_mock_modeled_area_feature(
    area_id: str = "omraden.30125",
    omrade_id: int = 30125,
    coordinates: list[list[list[list[float]]]] | None = None,
) -> dict[str, Any]:
    """Create a single mock modeled groundwater area feature."""
    if coordinates is None:
        # Simple polygon around Gothenburg area
        coordinates = [
            [
                [
                    [11.8, 57.6],
                    [12.2, 57.6],
                    [12.2, 57.8],
                    [11.8, 57.8],
                    [11.8, 57.6],
                ]
            ]
        ]

    return {
        "type": "Feature",
        "id": area_id,
        "geometry": {"type": "MultiPolygon", "coordinates": coordinates},
        "properties": {
            "omrade_id": omrade_id,
            "name": f"Area_{omrade_id}",
            "description": "Modeled groundwater area",
        },
        "links": [
            {
                "href": f"https://resource.sgu.se/service/grundvattenmodell/collections/omraden/items/{area_id}",
                "rel": "self",
                "type": "application/geo+json",
                "title": "This document",
            }
        ],
    }


def create_mock_modeled_level_feature(
    level_id: str = "grundvattennivaer-tidigare.1",
    omrade_id: int = 30125,
    datum: str = "2024-08-01Z",
    objectid: int = 1,
    date: datetime | None = None,
) -> dict[str, Any]:
    """Create a single mock modeled groundwater level feature."""
    if date is None:
        date = datetime(2024, 8, 1, tzinfo=UTC)

    return {
        "type": "Feature",
        "id": level_id,
        "geometry": {"type": "Point", "coordinates": [11.9746, 57.7089]},
        "properties": {
            "omrade_id": omrade_id,
            "datum": datum,
            "objectid": objectid,
            "date": date.isoformat(),
            "grundvattensituation_sma": 45,
            "grundvattensituation_stora": 53,
            "fyllnadsgrad_sma": 68,
            "fyllnadsgrad_stora": 72,
            "area_name": f"Area_{omrade_id}",
        },
        "links": [
            {
                "href": f"https://resource.sgu.se/service/grundvattenmodell/collections/grundvattennivaer-tidigare/items/{level_id}",
                "rel": "self",
                "type": "application/geo+json",
                "title": "This document",
            }
        ],
    }


def create_mock_modeled_area_collection_response(
    areas: list[dict[str, Any]] | None = None,
    number_returned: int | None = None,
    number_matched: int | None = None,
) -> dict[str, Any]:
    """Create a mock ModeledAreaCollection response."""
    if areas is None:
        areas = [create_mock_modeled_area_feature()]

    if number_returned is None:
        number_returned = len(areas)

    if number_matched is None:
        number_matched = number_returned

    return {
        "type": "FeatureCollection",
        "features": areas,
        "numberReturned": number_returned,
        "numberMatched": number_matched,
        "timeStamp": "2024-09-21T10:30:00Z",
        "links": [
            {
                "href": "https://resource.sgu.se/service/grundvattenmodell/collections/omraden/items",
                "rel": "self",
                "type": "application/geo+json",
                "title": "This document",
            }
        ],
    }


def create_mock_modeled_level_collection_response(
    levels: list[dict[str, Any]] | None = None,
    number_returned: int | None = None,
    number_matched: int | None = None,
) -> dict[str, Any]:
    """Create a mock ModeledGroundwaterLevelCollection response."""
    if levels is None:
        levels = [create_mock_modeled_level_feature()]

    if number_returned is None:
        number_returned = len(levels)

    if number_matched is None:
        number_matched = number_returned

    return {
        "type": "FeatureCollection",
        "features": levels,
        "numberReturned": number_returned,
        "numberMatched": number_matched,
        "timeStamp": "2024-09-21T10:30:00Z",
        "links": [
            {
                "href": "https://resource.sgu.se/service/grundvattenmodell/collections/grundvattennivaer-tidigare/items",
                "rel": "self",
                "type": "application/geo+json",
                "title": "This document",
            }
        ],
    }


def create_mock_single_modeled_area_response(
    area_id: str = "omraden.30125", omrade_id: int = 30125
) -> dict[str, Any]:
    """Create a mock response for getting a single modeled area by ID."""
    area = create_mock_modeled_area_feature(area_id=area_id, omrade_id=omrade_id)
    return create_mock_modeled_area_collection_response([area])


def create_mock_single_modeled_level_response(
    level_id: str = "grundvattennivaer-tidigare.1",
    omrade_id: int = 30125,
    datum: str = "2024-08-01Z",
    objectid: int = 1,
) -> dict[str, Any]:
    """Create a mock response for getting a single modeled level by ID."""
    level = create_mock_modeled_level_feature(
        level_id=level_id, omrade_id=omrade_id, datum=datum, objectid=objectid
    )
    return create_mock_modeled_level_collection_response([level])


def create_mock_multiple_modeled_areas_response(
    area_ids: list[int] | None = None, limit: int = 10
) -> dict[str, Any]:
    """Create a mock response for multiple modeled areas."""
    if area_ids is None:
        area_ids = [30125, 30126, 30127]

    areas = []
    for i, omrade_id in enumerate(area_ids[:limit]):
        area = create_mock_modeled_area_feature(
            area_id=f"omraden.{omrade_id}",
            omrade_id=omrade_id,
            coordinates=[
                [
                    [
                        [11.8 + i * 0.1, 57.6 + i * 0.1],
                        [12.2 + i * 0.1, 57.6 + i * 0.1],
                        [12.2 + i * 0.1, 57.8 + i * 0.1],
                        [11.8 + i * 0.1, 57.8 + i * 0.1],
                        [11.8 + i * 0.1, 57.6 + i * 0.1],
                    ]
                ]
            ],
        )
        areas.append(area)

    return create_mock_modeled_area_collection_response(
        areas=areas,
        number_returned=len(areas),
        number_matched=len(area_ids),
    )


def create_mock_multiple_modeled_levels_response(
    omrade_id: int = 30125,
    count: int = 5,
    start_date: datetime | None = None,
) -> dict[str, Any]:
    """Create a mock response for multiple modeled levels."""
    if start_date is None:
        start_date = datetime(2024, 1, 1, tzinfo=UTC)

    levels = []
    for i in range(count):
        level_date = start_date.replace(month=min(1 + i, 12))
        datum_str = level_date.strftime("%Y-%m-%dZ")
        level = create_mock_modeled_level_feature(
            level_id=f"grundvattennivaer-tidigare.{i + 1}",
            omrade_id=omrade_id,
            datum=datum_str,
            objectid=i + 1,
            date=level_date,
        )
        levels.append(level)

    return create_mock_modeled_level_collection_response(
        levels=levels, number_returned=count, number_matched=count
    )


def create_mock_empty_modeled_collection_response() -> dict[str, Any]:
    """Create a mock response for an empty modeled collection."""
    return create_mock_modeled_area_collection_response(
        areas=[], number_returned=0, number_matched=0
    )


# Groundwater chemistry mock responses (SGU grundvattenkvalitet v2 API)

CHEMISTRY_V2_BASE_URL = "https://api.sgu.se/oppnadata/grundvattenkvalitet-analysresultat-provplatser-v2/ogc/features/v1/"


def create_mock_sampling_site_feature(
    site_id: str = "provplatser.1560",
    platsbeteckning: str = "TTK-442-M",
    provplatsnamn: str = "Lena",
    nationellt_provplatsid: int = 359366,
    lanskod: str = "04",
    coordinates: list[float] | None = None,
) -> dict[str, Any]:
    """Create a single mock sampling site feature, based on a real v2 response."""
    if coordinates is None:
        coordinates = [16.68629857, 58.90889813]

    analyses_url = (
        f"{CHEMISTRY_V2_BASE_URL}collections/analysresultat/items"
        f"?filter=nationellt_provplatsid%20%3D%20'{nationellt_provplatsid}'"
    )
    return {
        "type": "Feature",
        "id": site_id,
        "geometry": {"type": "Point", "coordinates": coordinates},
        "properties": {
            "objectid": 1560,
            "nationellt_provplatsid": nationellt_provplatsid,
            "provplatsuuid": "c8942ea7-9708-4ba3-85c3-be4f84cd5e4b",
            "overvakningsstation": 362247,
            "platsbeteckning": platsbeteckning,
            "provplatsnamn": provplatsnamn,
            "dold_koordinat": "Nej",
            "e": 597131,
            "n": 6531132,
            "antal_prov": 3,
            "antal_provtillf": 2,
            "forstaprov": "2021-10-06Z",
            "senasteprov": "2021-10-06Z",
            "provtyper": "Grundvatten",
            "media": "Vatten",
            "lanskod": lanskod,
            "lan": "SÖDERMANLANDS LÄN",
            "kommunkod": "0482",
            "kommun": "FLEN",
            "vattendistrikt": "SE3",
            "vattendistrikt_tx": "Norra Östersjöns vattendistrikt",
            "eu_cd": "",
            "andra_beteckningar": None,
            "delaro_namn": "Utloppet av Långhalsen",
            "delaro_ms_cd": "WA33343004",
            "delaro_uuid": "1ED96C52-74DE-43F0-98FA-8C82D8A9E020",
            "vattenforekomst_aro_id": "SE79C9CECD-D622-4C7A-8BA1-5BE01E5F0B72",
            "huvudavrinningsomrade_id": 65000,
            "eucd_gwb": None,
            "positioneringsmetod": "GPS",
            "positioneringsmetod_tx": "koordinat från GPS",
            "positionskvalitet": None,
            "positionskvalitet_tx": None,
            "provplatstyp": "schaktbrunn",
            "provplatstyp_tx": "Grävd brunn",
            "provplatskat_bedgr": None,
            "provplatskat_bedgr_tx": None,
            "region_bdgr": "E",
            "region_bdgr_tx": "Mellansvenska sänkan",
            "refniva": None,
            "hojdsystem": None,
            "hojdsystem_tx": None,
            "hojdmetod": None,
            "hojdmetod_tx": None,
            "rorhojd": 0.35,
            "rorlangd": None,
            "borrhalslutning": None,
            "sillangd": None,
            "innerdiam": 1500,
            "material": "cement",
            "material_tx": "betong",
            "tecken_jorddjup": None,
            "jorddjup": None,
            "jordart": "SA",
            "jordart_tx": "sand",
            "jord_ovan_jord": None,
            "jord_ovan_jord_tx": None,
            "genes_jord": None,
            "genes_jord_tx": None,
            "bergart": None,
            "bergart_tx": None,
            "akvifer": "Ö",
            "akvifer_tx": "öppet magasin",
            "gvmiljo_bedgr": "4",
            "gvmiljo_bedgr_tx": "grundvattenmiljö 4: isälvsavlagringar",
            "geohylag": "M",
            "geohylag_tx": "intermediärt område",
            "etabldatum": "2021-10-06Z",
            "provtagningssyfte": "NMO_PMO",
            "provtagningssyften_tx": "Nat.MÖ -  Påverkade områden",
            "nationell": "ja",
            "regional": None,
            "symbol": "ovr",
            "analysdata_json": f"{analyses_url}&f=application/json",
            "analysdata_csv": f"{analyses_url}&f=text/csv",
        },
    }


def create_mock_analysis_result_feature(
    result_id: str = "analysresultat.1757",
    nationellt_provplatsid: int = 359366,
    provplatsnamn: str = "Lena",
    sampling_date: datetime | None = None,
    parameternamn: str = "Nitratkväve",
    ntlkemiparameterid: str = "CH02/102",
    matvardetal: float | None = 2.99,
    enhet: str = "mg.l-1",
    lanskod: int = 4,
) -> dict[str, Any]:
    """Create a single mock analysis result feature, based on a real v2 response."""
    if sampling_date is None:
        sampling_date = datetime(2021, 10, 6, tzinfo=UTC)

    return {
        "type": "Feature",
        "id": result_id,
        "geometry": None,
        "properties": {
            "objectid": 1757,
            "resultatid": 5865282,
            "leveransid": "F68864C5-A58F-4B3A-BDB6-B4FD4EFA8BB0",
            "ursprung": "db_grundvatten",
            "bestallare": "HaV",
            "bestallare_tx": "Havs- och vattenmyndigheten",
            "undersokningstyp": None,
            "bestalld_undersokning": None,
            "utfor_org": "Sveriges geologiska undersökning",
            "utfor_org_typ": None,
            "rapportnamn": None,
            "rapportnamn_diva": None,
            "diva_url": None,
            "nationellt_provplatsid": nationellt_provplatsid,
            "overvakningsstation": 362247,
            "provplatsuuid": "c8942ea7-9708-4ba3-85c3-be4f84cd5e4b",
            "provplatsnamn": provplatsnamn,
            "provplatstyp": "schaktbrunn",
            "lanskod": lanskod,
            "lan": "SÖDERMANLANDS LÄN",
            "kommunkod": "0482",
            "kommun": "FLEN",
            "e": 597131,
            "n": 6531132,
            "fkt_provpunkt_e": None,
            "fkt_provpunkt_n": None,
            "provtag_org": "Sveriges geologiska undersökning",
            "provtag_org_tx": None,
            "provtagningsdatum": sampling_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "provtagning_slutdatum": None,
            "provtagningssyfte": "NMO_PMO",
            "provtagningssyfte_tx": "Nat.MÖ -  Påverkade områden",
            "provtagningsmetod": None,
            "provtagningsmetod_url": None,
            "provdatatyp": "Grundvatten",
            "provplatsmiljo": "SJO-SOTV-RINN",
            "media": "vatten",
            "ackrediteradprovtagare": None,
            "direktbehandling": None,
            "direktbehandling_url": None,
            "filtrerat": None,
            "filterstorlek": None,
            "omsattningstid": None,
            "omsattningsvolym": None,
            "omsatt_tid_till_prov": None,
            "kommentar_prov": "",
            "laboratorium": None,
            "laboratorium_tx": None,
            "utforarlabbid": None,
            "utforarlabbid_tx": None,
            "provkodoriginal": "2021-13109",
            "rapportkodlabb": None,
            "registreringsdatum": None,
            "analysdatum": None,
            "provberedning": None,
            "provberedning_url": None,
            "provkarl": None,
            "provkarl_tx": None,
            "provlagring": None,
            "provlagring_tx": None,
            "ntlkemiparameterid": ntlkemiparameterid,
            "parameternamn": parameternamn,
            "parameter_anm": None,
            "parametergrupp": "Närsalter~Joner",
            "cas_kod": None,
            "matvardetext": None,
            "matvardetal": matvardetal,
            "matvardetal_anm": None,
            "enhet": enhet,
            "enhet_tx": "mg/l",
            "matvstd": None,
            "matvstd_tx": None,
            "loq": None,
            "lod": None,
            "matosakerhet": None,
            "matosakerhetenhet": None,
            "matosakerhetenhet_tx": None,
            "matosakerhettyp": None,
            "matosakerhettyp_tx": None,
            "matvardespar": None,
            "analysmetod": "Beräknad från NO3",
            "analysmetod_url": None,
            "ackrediteradmetod": None,
            "analysinstrument": None,
            "analysinstrument_url": None,
            "kommentar_matvarde": None,
            "vattentyp": "grundvatten",
            "vattentyp_tx": None,
            "kvalitetsflagga": None,
            "granskningskommentar": None,
        },
    }


def _create_mock_chemistry_collection_response(
    collection: str, features: list[dict[str, Any]]
) -> dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": features,
        "numberReturned": len(features),
        "numberMatched": len(features),
        "timeStamp": "2026-10-15T08:39:25.927Z",
        "links": [
            {
                "href": f"{CHEMISTRY_V2_BASE_URL}collections/{collection}/items",
                "rel": "self",
                "type": "application/geo+json",
                "title": "This document",
            }
        ],
    }


def create_mock_sampling_site_collection_response(
    sites: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a mock SamplingSiteCollection response."""
    if sites is None:
        sites = [create_mock_sampling_site_feature()]
    return _create_mock_chemistry_collection_response("provplatser", sites)


def create_mock_analysis_result_collection_response(
    results: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a mock AnalysisResultCollection response."""
    if results is None:
        results = [create_mock_analysis_result_feature()]
    return _create_mock_chemistry_collection_response("analysresultat", results)


def create_mock_multiple_sampling_sites_response(
    sites: list[tuple[str, str, int]] | None = None,
) -> dict[str, Any]:
    """Create a mock response for multiple sampling sites.

    Args:
        sites: List of (platsbeteckning, provplatsnamn, nationellt_provplatsid) tuples
    """
    if sites is None:
        sites = [("TTK-442-M", "Lena", 359366), ("SYD-681-C", "Tofta Bjärs", 378865)]

    return create_mock_sampling_site_collection_response(
        [
            create_mock_sampling_site_feature(
                site_id=f"provplatser.{i + 1}",
                platsbeteckning=platsbeteckning,
                provplatsnamn=provplatsnamn,
                nationellt_provplatsid=national_site_id,
            )
            for i, (platsbeteckning, provplatsnamn, national_site_id) in enumerate(
                sites
            )
        ]
    )


def create_mock_multiple_analysis_results_response(
    nationellt_provplatsid: int = 359366,
    parameters: list[tuple[str, str, float]] | None = None,
    start_date: datetime | None = None,
) -> dict[str, Any]:
    """Create a mock response for multiple analysis results, one month apart.

    Args:
        nationellt_provplatsid: National sampling site ID
        parameters: List of (parameternamn, ntlkemiparameterid, value) tuples
        start_date: Sampling date of the first result
    """
    if parameters is None:
        parameters = [
            ("pH", "CH11/62", 7.2),
            ("Nitratkväve", "CH02/102", 2.99),
            ("Klorid", "CH02/96", 8.3),
        ]

    if start_date is None:
        start_date = datetime(2020, 1, 1, tzinfo=UTC)

    return create_mock_analysis_result_collection_response(
        [
            create_mock_analysis_result_feature(
                result_id=f"analysresultat.{i + 1}",
                nationellt_provplatsid=nationellt_provplatsid,
                sampling_date=start_date.replace(month=min(1 + i, 12)),
                parameternamn=parameternamn,
                ntlkemiparameterid=parameter_id,
                matvardetal=value,
            )
            for i, (parameternamn, parameter_id, value) in enumerate(parameters)
        ]
    )


def create_mock_empty_chemistry_collection_response() -> dict[str, Any]:
    """Create a mock response for an empty chemistry collection."""
    return create_mock_sampling_site_collection_response(sites=[])
