# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
