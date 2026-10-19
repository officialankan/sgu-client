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

The GeoJSON structure is flattened:

- Each feature becomes a row.
- Point coordinates become `longitude` and `latitude` columns.
- Every property becomes a top-level column, using its English field name.
- Date columns are `datetime64[ns, UTC]`, even when every value is missing (`NaT`).
  See [Dates and times](getting_started.md#dates-and-times).
- Measurement, level and result collections are sorted by date (pass
  `sort_by_date=False` to keep the API order).

```text
# GeoJSON feature                                   # DataFrame row
{"geometry": {"type": "Point",                      longitude  latitude  station_id  ...
              "coordinates": [15.5, 58.3]},              15.5      58.3        95_2  ...
 "properties": {"platsbeteckning": "95_2", ...}}
```

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
