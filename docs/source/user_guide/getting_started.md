# Getting started

## Installation

`sgu-client` requires Python 3.11 or later.

```bash
uv add sgu-client
# or: pip install sgu-client
```

To convert responses to pandas DataFrames and Series, install the `recommended` extra:

```bash
uv add "sgu-client[recommended]"
# or: pip install "sgu-client[recommended]"
```

## Creating a client

{class}`~sgu_client.SGUClient` is the single entry point. Endpoints are grouped by
domain on its attributes:

| Attribute | Data |
| --- | --- |
| `client.levels.observed` | Measured groundwater levels from monitoring stations |
| `client.levels.modeled` | Modeled groundwater levels from SGU-HYPE |
| `client.chemistry` | Groundwater chemistry sampling sites and analysis results |

```python
from sgu_client import SGUClient

client = SGUClient()
station = client.levels.observed.get_station_by_name(station_id="95_2")
print(station.properties.station_name)
```

Use the client as a context manager to close the underlying HTTP session when you are
done:

```python
with SGUClient() as client:
    stations = client.levels.observed.get_stations(limit=10)
```

## Typed responses

Every method returns a typed [Pydantic](https://docs.pydantic.dev/) model, so your
editor can autocomplete fields. Collections follow the GeoJSON structure of the
underlying OGC API: a `features` list where each feature has a `geometry` and
`properties`.

```python
stations = client.levels.observed.get_stations(limit=5)

for station in stations.features:
    print(station.properties.station_name, station.properties.municipality)
    print(station.geometry.coordinates)
```

Fields have English names, and each maps to the Swedish name used by the SGU API (for
example `station_id` ↔ `platsbeteckning`). The {doc}`/api` lists the API name for every
field.

## Configuration

Pass an {class}`~sgu_client.SGUConfig` to change timeouts, retries or logging:

```python
from sgu_client import SGUClient, SGUConfig

config = SGUConfig(timeout=60, max_retries=5, log_level="DEBUG")
client = SGUClient(config=config)
```

See {class}`~sgu_client.SGUConfig` for all options and their defaults.

## Handling errors

All errors raised by the client inherit from {class}`~sgu_client.SGUClientError`:

```python
from sgu_client import SGUAPIError, SGUClientError, SGUTimeoutError

try:
    measurements = client.levels.observed.get_measurements_by_name(station_id="95_2")
except SGUTimeoutError:
    ...  # the request took longer than `timeout`
except SGUAPIError as err:
    print(err.status_code, err.response_data)
except SGUClientError:
    ...  # any other client error
```

Convenience lookups such as `get_station_by_name()` raise `ValueError` when the
arguments are invalid or the lookup is ambiguous.
