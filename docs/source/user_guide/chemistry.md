# Groundwater chemistry

`client.chemistry` gives access to SGU's *Grundvattenkvalitet, analysresultat och
provplatser (version 2)* API. The data comes as two collections:

- **Sampling sites** (*provplatser*): wells and springs where samples are taken.
- **Analysis results** (*analysresultat*): one measured value of one chemical
  parameter in one sample.

## Identifying sites

A sampling site has three identifiers:

| Argument | API name | Example |
| --- | --- | --- |
| `national_site_id` | `nationellt_provplatsid` | `359366` |
| `site_id` | `platsbeteckning` | `"TTK-442-M"` |
| `site_name` | `provplatsnamn` | `"Lena"` |

Analysis results refer to sites **only** by `national_site_id`, so that is the fastest
way to fetch results. Passing `site_id` or `site_name` instead works, but costs an extra
request to look up the site and logs a warning.

```python
from sgu_client import SGUClient

with SGUClient() as client:
    site = client.chemistry.get_sampling_site_by_name(site_id="TTK-442-M")
    national_site_id = site.properties.national_site_id  # 359366
```

## Fetching analysis results

Fetch results for one or more sites, optionally limited to a time range with `tmin` and
`tmax`:

```python
results = client.chemistry.get_results_by_site(
    359366,
    tmin="2020-01-01",
    tmax="2024-01-01",
)

# several sites in one request
results = client.chemistry.get_results_by_sites([359366, 378865], tmin="2020-01-01")
```

`sampling_date` and the other result dates are UTC datetimes, as are the site dates
`established_date`, `first_sample_date` and `latest_sample_date`. See
[Dates and times](getting_started.md#dates-and-times).

When sites are given by `site_id` or `site_name`, a lookup that misses any requested
site raises `ValueError` instead of returning partial results.

## Filtering by parameter

Parameters are identified by SGU's Swedish parameter names (`parameter_name`,
*parameternamn*). Some common ones:

| Parameter name | Meaning |
| --- | --- |
| `pH` | pH |
| `Konduktivitet` | Electrical conductivity |
| `Klorid` | Chloride |
| `Svavelsulfat` | Sulfate |
| `Nitratkväve` | Nitrate nitrogen |
| `Bly` | Lead |

```python
# all lead measurements since 2020
lead = client.chemistry.get_results_by_parameter("Bly", tmin="2020-01-01")

# pH at a single site
ph = client.chemistry.get_results_by_parameter("pH", national_site_id=359366)
```

## Querying the collections directly

For anything the convenience methods don't cover, query the collections with OGC API
filters. `filter_expr` takes a CQL expression using the Swedish API field names:

```python
sites = client.chemistry.get_sampling_sites(
    bbox=[12.0, 55.0, 16.0, 58.0],
    filter_expr="provplatstyp='brunn_ror'",
)

results = client.chemistry.get_analysis_results(
    filter_expr="parameternamn='Bly' AND provtagningsdatum>='2020-01-01'",
)
```

```{note}
The v2 chemistry API ignores the `sortby` parameter.
```
