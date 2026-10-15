# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- **pandas**: `pivot_by_parameter()` pivots on `parameter_name` by default; `to_dataframe()` parses `sampling_date`, `sampling_end_date`, `registration_date` and `analysis_date` (results) and `established_date`, `first_sample_date`, `latest_sample_date` (sites) as UTC datetimes

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
