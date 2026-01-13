# SGU Client

A modern Python client library for accessing Geological Survey of Sweden (SGU) groundwater data APIs with type safety and pandas integration.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![PyPI version](https://badge.fury.io/py/sgu-client.svg)](https://badge.fury.io/py/sgu-client)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/officialankan/sgu-client/branch/main/graph/badge.svg)](https://codecov.io/gh/officialankan/sgu-client)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Security Scanning](https://github.com/officialankan/sgu-client/actions/workflows/security.yml/badge.svg)](https://github.com/officialankan/sgu-client/actions/workflows/security.yml)

> This package is not affiliated with or endorsed by SGU.

## Features

- **Type-safe**: Full type hints with Pydantic validation
- **Pandas integration**: Convert data to DataFrames or Series with optional pandas dependency
- **Friendly shortcuts**: Convenience functions to access stations by names, modeled levels by coordinates, and much more.

Get going with your analysis in just a few lines of code:

```python
from sgu_client import SGUClient

with SGUClient() as client:
    measurements = client.levels.observed.get_measurements_by_name(station_id="95_2")
    df = measurements.to_dataframe()

# ... rest of your awesome workflow
```

## Installation

Using `uv`

```bash
# basic installation
uv add sgu-client

# with pandas support for dataframe conversion
uv add "sgu-client[recommended]"
```

... or using `pip`

```bash
# basic installation
pip install sgu-client

# with pandas support for dataframe conversion
pip install "sgu-client[recommended]"
```

## Usage

### Initializing a client

```python
from sgu_client import SGUClient

client = SGUClient()

# with custom configuration
from sgu_client import SGUConfig
config = SGUConfig(timeout=60, debug=True, max_retries=5)
client = SGUClient(config=config)

# as a context manager
with SGUClient() as client:
    stations = client.levels.observed.get_stations(limit=10)
```

### Observed groundwater levels

Access real-time and historical groundwater monitoring data from SGU's network of observation stations.

```python
from sgu_client import SGUClient
from datetime import UTC, datetime


with SGUClient() as client:
    # basic API endpoint usage
    stations = client.levels.observed.get_stations(limit=50)
    
    # with OGC API filters, like bbox of southern Sweden
    stations = client.levels.observed.get_stations(
        bbox=[12.0, 55.0, 16.0, 58.0],
        limit=100
    )

    # or filter expressions
    stations = client.levels.observed.get_stations(
        bbox=[12.0, 55.0, 16.0, 58.0],
        filter_expr="akvifer='JS'",
        limit=100
    )
    
    # convenience function to get station by name
    station = client.levels.observed.get_station_by_name(
        station_id="95_2"  # or station_name="Lagga_2"
    )
    # or multiple stations by names
    stations = client.levels.observed.get_stations_by_names(
        station_id=["95_2", "101_1"]  # or station_name=["Lagga_2", ...]
    )

    # convenience function to get measurements by station name
    measurements = client.levels.observed.get_measurements_by_name(
        station_id="95_2",  # or station_name="Lagga_2"
        limit=100
    )
    # or multiple stations by names
    measurements = client.levels.observed.get_measurements_by_names(
        station_id=["95_2", "101_1"],  # or station_name=["Lagga_2", ...]
        limit=100
    )

    # filter by datetime for faster responses
    tmin = datetime(2020, 1, 1, tzinfo=UTC)
    tmax = datetime(2021, 1, 1, tzinfo=UTC)
    measurements = client.levels.observed.get_measurements_by_names(
        station_id=["95_2"], tmin=tmin, tmax=tmax, limit=10
    )
    
    # responses that create lists of features can be converted to pandas DataFrames
    measurements = client.levels.observed.get_measurements_by_names(
        station_id=["95_2", "101_1"],  # or station_name=["Lagga_2", ...]
        limit=100
    )
    df = measurements.to_dataframe()  
    # or series
    series = measurements.to_series()  # defaults to 'water_level_masl_m' (head) column with datetime index
```

### Modeled groundwater levels

Access modeled groundwater levels from SGU-HYPE.

```python
from sgu_client import SGUClient

with SGUClient() as client:
    # basic API endpoint usage
    areas = client.levels.modeled.get_areas(limit=10)
    
    # with OGC API filters, like bbox of southern Sweden
    areas = client.levels.modeled.get_areas(
        bbox=[12.0, 55.0, 16.0, 58.0],
        limit=20
    )
    
    # get a specific area by ID
    area = client.levels.modeled.get_area("omraden.30125")
    print(f"Area ID: {area.properties.area_id}")
    print(f"Geometry: {area.geometry.type}")
    
    # convenience function to get levels for a specific area
    levels = client.levels.modeled.get_levels_by_area(30125, limit=10)
    # or multiple areas by IDs
    levels = client.levels.modeled.get_levels_by_areas(
        area_ids=[30125, 30126],
        limit=50
    )

    # convenience function to get levels by coordinates
    levels = client.levels.modeled.get_levels_by_coords(
        lat=57.7089,
        lon=11.9746,
        limit=10
    )
    
    # responses that create lists of features can be converted to pandas DataFrames
    levels = client.levels.modeled.get_levels_by_areas(
        area_ids=[30125, 30126],
        limit=50
    )
    df = levels.to_dataframe()
    # or series
    series = levels.to_series()  # defaults to 'relative_level_small_resources' column with datetime index
```

### Groundwater Chemistry

Access groundwater chemistry data including sampling sites and chemical analysis results.

```python
from sgu_client import SGUClient
from datetime import UTC, datetime

with SGUClient() as client:
    # basic API endpoint usage
    sites = client.chemistry.get_sampling_sites(limit=50)

    # with OGC API filters, like bbox of southern Sweden
    sites = client.chemistry.get_sampling_sites(
        bbox=[12.0, 55.0, 16.0, 58.0],
        limit=100
    )

    # and filter expressions
    sites = client.chemistry.get_sampling_sites(
        bbox=[12.0, 55.0, 16.0, 58.0],
        filter_expr="provplatstyp='jordbrunn'",
        limit=100
    )

    # convenience function to get site by name
    site = client.chemistry.get_sampling_site_by_name(
        site_id="10001_1"  # or site_name="Ringarum_1"
    )
    # or multiple sites by names
    sites = client.chemistry.get_sampling_sites_by_names(
        site_id=["10001_1", "10002_1"]  # or site_name=["Ringarum_1", ...]
    )

    # get chemical analysis results
    results = client.chemistry.get_analysis_results(limit=100)

    # convenience function to get results for a specific site
    results = client.chemistry.get_results_by_site(
        site_id="1000_1",  # or site_name="Ringarum_1"
        limit=100
    )
    # or multiple sites by names
    results = client.chemistry.get_results_by_sites(
        site_id=["1000_1", "1001_2"],  # or site_name=["Ringarum_1", ...]
        limit=100
    )

    # filter by datetime for faster responses
    tmin = datetime(2020, 1, 1, tzinfo=UTC)
    tmax = datetime(2021, 1, 1, tzinfo=UTC)
    results = client.chemistry.get_results_by_site(
        station_id="1000_1", tmin=tmin, tmax=tmax, limit=500
    )

    # filter by chemical parameter
    ph_results = client.chemistry.get_results_by_parameter(
        parameter="PH",
        station_id="1000_1",
        tmin=tmin,
        tmax=tmax
    )

    # responses that create lists of features can be converted to pandas DataFrames
    results = client.chemistry.get_results_by_site(
        station_id="1000_1",
        limit=1000
    )
    df = results.to_dataframe()
    # or series
    series = results.to_series()  # defaults to 'measurement_value' column with sampling_date index
    # or pivot by parameter for multi-parameter analysis
    df_pivot = results.pivot_by_parameter()  # creates columns like 'PH', 'NITRAT', 'KLORID', etc.
```

### Working with Typed Data

All responses are fully typed with Pydantic models:

```python
from sgu_client import SGUClient

client = SGUClient()

# Get stations with full type safety
stations = client.levels.observed.get_stations(limit=5)

for station in stations.features:
    # All properties are typed and documented
    print(f"Station: {station.properties.station_name}")
    print(f"Municipality: {station.properties.municipality}")
    print(f"Coordinates: {station.geometry.coordinates}")

# Get measurements with automatic datetime parsing
measurements = client.levels.observed.get_measurements(limit=5)
for measurement in measurements.features:
    props = measurement.properties
    print(f"Date: {props.observation_datetime}")  # Parsed datetime object
    print(f"Level: {props.water_level_masl_m} m above sea level")
```

## API Reference

### SGUClient

The main client class providing access to all SGU APIs.

- `levels.observed` - Observed groundwater level measurements
- `levels.modeled` - Modeled groundwater levels from SGU-HYPE
- `chemistry` - Groundwater chemistry sampling sites and analysis results

### Configuration

```python
from sgu_client import SGUConfig

config = SGUConfig(
    timeout=30,        # Request timeout in seconds
    max_retries=3,     # Maximum retry attempts
    debug=False        # Enable debug logging
)
```

## Development

We recommend using [uv](https://github.com/astral-sh/uv) for development:

```bash
# Clone the repository
git clone https://github.com/officialankan/sgu-client.git
cd sgu-client

# Install dependencies and sync environment
uv sync --all-extras

# Run tests
uv run pytest

# Format and lint code
uv run ruff format
uv run ruff check --fix
```

### Release Process

To release a new version:

1. Create PR with your changes + version bump in `pyproject.toml`
2. PR will be tested and published to TestPyPI for verification
3. Once merged, the new version is automatically published to PyPI

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Roadmap

- [x] Initial release with observed and modeled groundwater levels
- [ ] Add example notebooks and tutorials
- [x] Add support for groundwater chemistry API
- [ ] Add support for geological data API

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Sveriges geologiska undersökning (SGU)](https://www.sgu.se/) for providing open access to groundwater data
- Built with [uv](https://github.com/astral-sh/uv), [Pydantic](https://pydantic.dev/), and [requests](https://requests.readthedocs.io/)
