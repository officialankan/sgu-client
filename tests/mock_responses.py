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
            "platsbeteckning": platsbeteckning,
            "obsdatum": observation_date.isoformat(),
            "observation_date": observation_date.isoformat(),
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
