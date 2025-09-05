# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/username/sgu-client/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/username/sgu-client/releases/tag/v0.1.0
