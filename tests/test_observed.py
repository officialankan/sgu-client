"""Basic tests for observed groundwater levels endpoints."""

from sgu_client import SGUClient
from sgu_client.models.observed import GroundwaterMeasurement, GroundwaterStation

TEST_STATION_ID = "stationer.4086"
TEST_STATION_PLATSBETECKNING = "95_2"
TEST_STATION_OBSPLATSNAMN = "Lagga_2"
TEST_MEASUREMENT_ID = "nivaer.1"
TEST_MEASUREMENT_METOD_FOR_M = "klucklod"
TEST_STATIONS_FILTER = "platsbeteckning in ('95_2', '101_1')"


def test_create_basic_client() -> None:
    client = SGUClient()
    assert hasattr(client, "observed_levels")


def test_get_lagga_station_by_id() -> None:
    client = SGUClient()
    station = client.observed_levels.get_station(TEST_STATION_ID)
    assert station is not None
    assert isinstance(station, GroundwaterStation)
    assert station.id == TEST_STATION_ID
    assert station.properties.platsbeteckning == TEST_STATION_PLATSBETECKNING
    assert station.properties.obsplatsnamn == TEST_STATION_OBSPLATSNAMN


def test_get_measurement_by_id() -> None:
    client = SGUClient()
    measurement = client.observed_levels.get_measurement(TEST_MEASUREMENT_ID)
    assert isinstance(measurement, GroundwaterMeasurement)
    assert measurement.id == TEST_MEASUREMENT_ID
    assert measurement.properties.metod_for_matning == TEST_MEASUREMENT_METOD_FOR_M


def test_stations_to_dataframe() -> None:
    client = SGUClient()
    stations = client.observed_levels.get_stations(filter_expr=TEST_STATIONS_FILTER)
    assert stations is not None
    df = stations.to_dataframe()
    assert not df.empty
    assert "platsbeteckning" in df.columns
    assert "obsplatsnamn" in df.columns
    assert all(
        station in df["platsbeteckning"].tolist() for station in ["95_2", "101_1"]
    )
