# Working with pandas

Collections can be converted to pandas objects. This needs the `recommended` extra:

```bash
uv add "sgu-client[recommended]"
# or: pip install "sgu-client[recommended]"
```

Without pandas installed, the conversion methods raise a
{class}`~sgu_client.utils.pandas_helpers.PandasImportError` explaining how to install it.

## DataFrames

`to_dataframe()` returns one row per feature:

```python
from sgu_client import SGUClient

with SGUClient() as client:
    measurements = client.levels.observed.get_measurements_by_names(
        station_id=["95_2", "101_1"],
        tmin="2020-01-01",
    )

df = measurements.to_dataframe()
df.groupby("station_id")["water_level_masl_m"].mean()
```

The GeoJSON structure is flattened the same way for every collection:

- Each feature becomes a row. The index is the row's position in the API response.
- The first column is `feature_id`, SGU's id for the feature (e.g. `stationer.4086`).
- Next come the collection's geometry columns, if it has any (see below).
- Then every property becomes a column, using its English field name, in the order of
  the properties model.
- Date columns are `datetime64[ns, UTC]`, even when every value is missing (`NaT`).
  See [Dates and times](getting_started.md#dates-and-times).
- An empty collection gives an empty DataFrame that still has all of these columns.

```text
# GeoJSON feature                          # DataFrame row
{"id": "stationer.4086",                   feature_id      longitude  latitude  station_id  ...
 "geometry": {"type": "Point",             stationer.4086       15.5      58.3        95_2  ...
              "coordinates": [15.5, 58.3]},
 "properties": {"platsbeteckning": "95_2", ...}}
```

## How the collections differ

Which geometry columns a collection has, whether it is sorted, and whether it has
`to_series()` depends on the collection, never on what a particular response contains:

| Collection | Geometry columns | Sorted by | `to_series()` |
| --- | --- | --- | --- |
| Observed stations | `longitude`, `latitude` | — | — |
| Observed measurements | — | `observation_date` | ✓ |
| Modeled areas | `centroid_longitude`, `centroid_latitude` | — | — |
| Modeled levels | — | `date` | ✓ |
| Sampling sites | `longitude`, `latitude` | — | — |
| Analysis results | — | `sampling_date` | ✓ |

- Point coordinates are null for stations and sites that SGU publishes without a
  location.
- Areas are square grid cells. SGU sends only each cell's outline, so sgu-client
  computes `centroid_longitude`/`centroid_latitude` as the centre of the cell. Modeled
  levels have no geometry of their own: join them to areas on `area_id` to map them.
- The sorted collections take `sort_by_date` (default `True`). Rows with the same date
  keep their API order, and the index stays the API position, so
  `to_dataframe(sort_by_date=False)` or `df.sort_index()` gives the API order back.
- Analysis results also have `pivot_by_parameter()`; see below.

## Series

Measurement, modeled level and analysis result collections also have `to_series()`,
which returns a time series indexed by date:

| Collection | Default index | Default values |
| --- | --- | --- |
| Observed measurements | `observation_date` | `water_level_masl_m` |
| Modeled levels | `date` | `relative_level_small_resources` |
| Analysis results | `sampling_date` | `measurement_value` |

```python
s = measurements.to_series()
s.plot()

# choose other columns
s = measurements.to_series(data="water_level_below_ground_m")
```

## One column per chemical parameter

{meth}`~sgu_client.models.chemistry.AnalysisResultCollection.pivot_by_parameter` turns
analysis results into a wide DataFrame with one column per parameter, indexed by
sampling date:

```python
results = client.chemistry.get_results_by_site(359366, tmin="2015-01-01")
wide = results.pivot_by_parameter()
wide[["pH", "Klorid", "Nitratkväve"]].plot(subplots=True)
```
