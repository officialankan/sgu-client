# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `SGUClient(transport=...)` sends requests through a transport of your own, for example canned responses in your tests. `Transport`, `TransportResponse` and the default `RequestsTransport` are exported from `sgu_client` (#59)
- `FeatureCollection` and `TimeSeriesCollection`, the shared bases of the six collection models, and `Feature`, the shared base of their features, exported from `sgu_client.models`. `TimeSeriesCollection` (measurements, modeled levels, analysis results) adds sorting by date and `to_series()` (#60)
- The pandas user guide has a table of how the collections' DataFrames differ (#60)

### Changed

- `ModeledArea.geometry` may be `None`, like every other feature's geometry; it used to be required (#60)
- Chemistry lookups raise `SGUNotFoundError` when a site isn't found, and `SGUAmbiguousError` when a `site_id` or `site_name` given to a single-site method such as `get_results_by_site()` matches several sites. They used to raise a plain `ValueError`; both are still `ValueError`s (#61)
- Observed and chemistry lookups word their errors and the extra-request warning the same way, e.g. `Exactly one of 'station_id' or 'station_name' must be provided.` instead of `Either 'station_id' or 'station_name' must be provided.` / `Only one of ...`. Passing more than one of `national_site_id`, `site_id` and `site_name` to `get_results_by_parameter()` says `At most one of ...` (#61)

### Fixed

- `GroundwaterStationCollection.to_dataframe()` keeps the feature id instead of overwriting it with the station id (#58)
- `to_dataframe()` on an empty measurement collection returns an empty DataFrame instead of raising `KeyError` (#60)
- Modeled area `centroid_longitude`/`centroid_latitude` are the centre of the grid cell. The ring's repeated closing corner was counted twice, which put the centroid about 500 m off-centre (#60)
- Rows with the same date keep their API order when sorted by date, e.g. the parameters of one chemistry sample (#60)
- Every collection accepts `totalFeatures: "unknown"`, not just the modeled ones (#60)

### Removed

- `BaseClient.post()` and the `data` and `**kwargs` arguments of the internal `BaseClient`; nothing used them (#59)

### BREAKING CHANGES

- **DataFrame columns are the same shape for every collection**: `feature_id`, then the collection's geometry columns, then the properties in model order. An empty collection keeps all these columns. See the pandas user guide for each collection's geometry columns (#60)

  | Collection | Before | After |
  | --- | --- | --- |
  | Stations | `station_id` held the station id (the feature id was lost), `geometry_type` | `feature_id` + `station_id`; no `geometry_type` |
  | Measurements | `measurement_id`, `observation_date` second; `geometry_type`/`longitude`/`latitude` when the response had geometry | `feature_id`; `observation_date` in model order; no geometry columns |
  | Modeled areas | `geometry_type` | no `geometry_type` |
  | Modeled levels | `level_id` | `feature_id` |
  | Sampling sites | `geometry_type`/`longitude`/`latitude` only when the response had geometry | `longitude`/`latitude` always, null without geometry; no `geometry_type` |
  | Analysis results | `geometry_type`/`longitude`/`latitude` when the response had geometry | no geometry columns |

- **`SGUResponse.to_dataframe()` removed**: it only raised `NotImplementedError`. Every collection gets `to_dataframe()` from `FeatureCollection` (#60)
- **`CRS` and `Link` are no longer importable from `sgu_client.models.observed`**, which only re-exported them by accident. Import them from `sgu_client.models.shared` (#60)
- **Observed lookups raise for stations that aren't found** instead of leaving them out. `get_stations_by_names()` (with `station_id` or `station_name`) and `get_measurements_by_name(s)()` with `station_name` raise `SGUNotFoundError` naming the missing stations, as chemistry already did for sites. `get_measurements_by_name(s)()` with `station_id` is unchanged (#61)

## [0.7.0] - 2026-10-20

### Added

- `SGUNotFoundError` and `SGUAmbiguousError`, raised when a lookup matches no feature or several. Both subclass `ValueError`, so existing `except ValueError` code keeps working (#62)
- **Modeled levels**: `get_levels_by_area()`, `get_levels_by_areas()` and `get_levels_by_coords()` take `tmin` and `tmax` (ISO strings or `datetime` objects), filtering on the level's date like the observed measurement lookups (#62)
- `get_measurements()`, `get_levels()` and `get_analysis_results()` take `tmin` and `tmax` too, filtering on the observation, level or sampling date. Docs and examples now use `tmin`/`tmax` instead of the OGC `datetime` interval (#62)

### Changed

- **Filter text**: a single value is sent as `field=value` and several as `field in (...)` on every dataset. Modeled area filters were `omrade_id = 1` / `omrade_id IN (1, 2)`, and observed sent one-element lists as `in (...)`. Same results, different filter text (#62)

### Fixed

- `get_station_by_name()` raises `SGUNotFoundError` instead of a bare `IndexError` when no station matches (#57)
- Single quotes in station, site or parameter names are escaped in filters instead of producing an invalid query (#62)

### BREAKING CHANGES

- **`SGUConfig.base_url`** is now the root of SGU's open data APIs (`https://api.sgu.se/oppnadata/`) and applies to the observed, modeled and chemistry datasets alike. It used to be the full observed-levels URL and was ignored by the other two. If you set it, drop the `grundvattennivaer-observerade/ogc/features/v1/` suffix (#62)
- **Internal URL constants removed**: `BASE_PATH` on the three clients, `ModeledGroundwaterLevelClient.MODELED_BASE_URL` and `GroundwaterChemistryClient.CHEMISTRY_BASE_URL`. Dataset URLs now come from `SGUConfig.base_url` (#62)

## [0.6.0] - 2026-10-19

### Added

- **Python 3.14**: supported and tested in CI (#48)
- `SGUClient.close()` closes the HTTP session for clients created without a `with` block
- **Type checking**: the package's type hints are now verified with [ty](https://github.com/astral-sh/ty) on every supported Python version, so editors and type checkers see accurate types (#45)

### Changed

- **Documentation**: restructured into User Guide, API Reference and About sections; the README is now a short landing page that links to the docs (#44)

### Fixed

- Methods wrapped by `optional_pandas_method` keep their original signature and docstring
- Stale docstring examples (the removed `debug` config option, an API alias passed as a keyword, an invalid date)
- Station `active_since` and `active_until` are no longer raw strings like `"2018-12-10Z"` (#49)
- **pandas 3**: date columns stay `datetime64[ns, UTC]`; pandas 3 otherwise picks the resolution per column (`us`, or `s` when every value is missing)

### BREAKING CHANGES

- **Dates are parsed everywhere** (#51): every date field on the observed, modeled and chemistry models, and `timeStamp` on every collection, is now a timezone-aware `datetime` in UTC instead of a string. Date-only values (`"1996-04-29Z"`) become midnight UTC. Values that can't be parsed, or have no timezone, become `None` and log a warning
- **Helper properties removed**: `observation_datetime`, `last_updated_datetime`, `date_parsed`, `established_datetime` and `sampling_datetime`; use the fields themselves
- **pandas**: every date column is `datetime64[ns, UTC]`, even when all values are missing. Modeled `date` was timezone-naive and station dates were strings. Measurement DataFrames no longer have the duplicate `last_update` column; use `last_updated`
- **`to_dict()`** returns `datetime` objects for date fields; use `model_dump_json()` for JSON

## [0.5.0] - 2026-10-15

### Changed

- **Groundwater chemistry API v2**: `client.chemistry` now uses SGU's `grundvattenkvalitet-analysresultat-provplatser-v2` dataset; the previous dataset no longer publishes any collections (#42)

### BREAKING CHANGES

- **Chemistry models**: `SamplingSiteProperties` and `AnalysisResultProperties` now type every v2 field. Fields that kept their meaning keep their attribute names (e.g. `parameter_name`, `sampling_date`, `analyses_csv_url`); fields SGU removed are gone:
  - Sampling sites: `well_depth`, `well_depth_qualifier`, `filter_depth_top`, `filter_depth_bottom`, `filter_depth_qualifier`, `decommissioned_date` (and `decommissioned_datetime`), `program_affiliation`, `local_monitoring`
  - Analysis results: `station_id`, `sample_id`, `sample_type`, `program_name`, `program_id`, `monitoring_manual`, `submission_date` (and `submission_datetime`), `parameter_short_name`, `parameter_sequence_number`, `water_preparation`, `reporting_limit`, `last_updated` (and `last_updated_datetime`), `row_number`
  - `detection_limit` is now a string, as returned by the API
- **County codes**: `county_code` is a zero-padded two-digit string on both sites and results (the v2 API mixes `"04"` and `4`); on analysis results it now maps to `lanskod` instead of `lan` (county name, see `county`)
- **Results by site**: analysis results no longer carry `platsbeteckning`, so `get_results_by_site()` and `get_results_by_sites()` take `national_site_id` as their first argument. `site_id` and `site_name` still work, but cost an extra lookup request and log a warning. Lookups that miss any requested site raise `ValueError`
- **Results by parameter**: `get_results_by_parameter()` matches SGU's parameter name (`parameternamn`, e.g. `"Bly"`, `"pH"`), and its site filter accepts `national_site_id`, `site_id` or `site_name` like `get_results_by_site()`
- **Site lookups**: `get_sampling_sites_by_names()` raises `ValueError` naming any requested sites that are not found, instead of returning a partial collection
- **pandas**: the feature ID column in chemistry `to_dataframe()` output is now `feature_id` (previously `site_id` for sites and `result_id` for results, which clashed with the new `result_id` field); `pivot_by_parameter()` pivots on `parameter_name` by default; `to_dataframe()` parses `sampling_date`, `sampling_end_date`, `registration_date` and `analysis_date` (results) and `established_date`, `first_sample_date`, `latest_sample_date` (sites) as UTC datetimes

### Added

- `national_site_id` option for `get_sampling_site_by_name()` and `get_sampling_sites_by_names()`

## [0.2.0] - 2025-09-11

### Added

- **Pagination Support**: Automatic handling of SGU API pagination for large datasets (#11)
- **Collection Series Export**: New `to_series()` convenience method for converting collections to pandas Series (#7)
- **Comprehensive Model Tests**: Complete test coverage for all Pydantic data models (#9)

### Enhanced

- **Developer Experience**: Made pytest coverage optional for faster development cycles (#10)
- **Documentation**: Added coverage badge and improved GitFlow-lite workflow documentation (#3)

### Fixed

- **API Response Handling**: Improved pagination handling for SGU API responses to prevent data loss
- **Test Performance**: Streamlined testing workflow for better development experience

## [0.1.0] - 2025-09-05

### Added

- Initial release of sgu-client
- Complete SGU groundwater data API client with type safety
- Hierarchical API structure with `client.levels.observed` and `client.levels.modeled`

### Key Features

- **Type Safety**: Full type hints with Pydantic validation
- **API Coverage**: Complete implementation of SGU groundwater levels API
- **Data Analysis**: Convert collections to pandas DataFrames
- **Performance**: Automatic warnings for slower operations
- **Extensibility**: Easy to add new SGU API endpoints
- **Developer Experience**: Modern tooling with ruff, pytest, and uv

[Unreleased]: https://github.com/username/sgu-client/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/username/sgu-client/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/username/sgu-client/releases/tag/v0.1.0
