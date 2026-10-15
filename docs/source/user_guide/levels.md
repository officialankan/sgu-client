# Groundwater levels

SGU publishes two kinds of groundwater level data, both available under `client.levels`:

- **Observed** levels (`client.levels.observed`) are measurements from SGU's network of
  monitoring stations.
- **Modeled** levels (`client.levels.modeled`) are estimates from the SGU-HYPE
  model, for model areas covering Sweden.

## Observed levels

### Finding stations

Look up a station by its identifier (`station_id`, *platsbeteckning*) or its name
(`station_name`, *obsplatsnamn*):

```python
from sgu_client import SGUClient

client = SGUClient()

station = client.levels.observed.get_station_by_name(station_id="95_2")
# or several at once
stations = client.levels.observed.get_stations_by_names(station_id=["95_2", "101_1"])
```

To search for stations, use {meth}`~sgu_client.client.levels.observed.ObservedGroundwaterLevelClient.get_stations`
with the filters described in [Filtering](#filtering):

```python
# stations in southern Sweden
stations = client.levels.observed.get_stations(
    bbox=[12.0, 55.0, 16.0, 58.0],
    limit=50,
)
```

### Fetching measurements

Fetch the measurements for one or more stations, optionally limited to a time range with
`tmin` and `tmax` (ISO strings or `datetime` objects):

```python
measurements = client.levels.observed.get_measurements_by_name(
    station_id="95_2",
    tmin="2024-10-01",
    tmax="2025-09-30",
)

# several stations in one request
measurements = client.levels.observed.get_measurements_by_names(
    station_id=["95_2", "101_1"],
    tmin="2020-01-01",
)
```

Each measurement has levels in metres above sea level (`water_level_masl_m`) and below
ground (`water_level_below_ground_m`). See
{class}`~sgu_client.models.observed.GroundwaterMeasurementProperties` for all fields.

## Modeled levels

Modeled levels are published per model area. Find areas by location, then fetch their
levels:

```python
areas = client.levels.modeled.get_areas(bbox=[12.0, 55.0, 16.0, 58.0], limit=10)

levels = client.levels.modeled.get_levels_by_areas(
    [area.properties.area_id for area in areas.features],
    datetime="2024-01-01/2025-01-01",
)
```

If you have a coordinate rather than an area,
{meth}`~sgu_client.client.levels.modeled.ModeledGroundwaterLevelClient.get_levels_by_coords`
finds the areas near it for you:

```python
# Gothenburg
levels = client.levels.modeled.get_levels_by_coords(lat=57.7089, lon=11.9746)
```

Modeled values are given as percentiles (0–100), separately for small and large
groundwater resources. See
{class}`~sgu_client.models.modeled.ModeledGroundwaterLevelProperties` for all fields.

## Filtering

The general query methods (`get_stations()`, `get_measurements()`, `get_areas()`,
`get_levels()`) accept the standard OGC API filters:

| Parameter | Description |
| --- | --- |
| `bbox` | Bounding box as `[min_lon, min_lat, max_lon, max_lat]` |
| `datetime` | ISO 8601 datetime or interval, e.g. `"2024-01-01/2025-01-01"` |
| `filter_expr` | CQL filter using the Swedish API field names, e.g. `"akvifer='JS'"` |
| `limit` | Maximum number of features to return |

Results are paginated automatically, so `limit` can be larger than the API's page size.
The convenience methods (`get_*_by_name()`, `get_levels_by_*()`) build these filters for
you, and forward any extra keyword arguments such as `limit` or `datetime`.
