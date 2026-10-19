# SGU Client

A modern Python client library for accessing Geological Survey of Sweden (SGU) groundwater data APIs with type safety and pandas integration.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![PyPI version](https://badge.fury.io/py/sgu-client.svg)](https://badge.fury.io/py/sgu-client)
[![Documentation](https://img.shields.io/badge/docs-github%20pages-blue.svg)](https://officialankan.github.io/sgu-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/officialankan/sgu-client/branch/main/graph/badge.svg)](https://codecov.io/gh/officialankan/sgu-client)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Security Scanning](https://github.com/officialankan/sgu-client/actions/workflows/security.yml/badge.svg)](https://github.com/officialankan/sgu-client/actions/workflows/security.yml)

> This package is not affiliated with or endorsed by SGU.

## Features

- **Observed and modeled groundwater levels**, plus **groundwater chemistry**
- **Type-safe**: full type hints with Pydantic validation
- **Pandas integration**: convert responses to DataFrames or Series with optional pandas dependency
- **Friendly shortcuts**: look up stations by name, modeled levels by coordinates, and much more

Get going with your analysis in just a few lines of code:

```python
from sgu_client import SGUClient

with SGUClient() as client:
    measurements = client.levels.observed.get_measurements_by_name(station_id="95_2")
    df = measurements.to_dataframe()

# ... rest of your awesome workflow
```

## Installation

```bash
uv add sgu-client
# or: pip install sgu-client

# with pandas support for dataframe conversion
uv add "sgu-client[recommended]"
# or: pip install "sgu-client[recommended]"
```

## Documentation

The full documentation lives at **[officialankan.github.io/sgu-client](https://officialankan.github.io/sgu-client/)**:

- [User Guide](https://officialankan.github.io/sgu-client/user_guide/index.html): getting started, groundwater levels, chemistry and pandas
- [API Reference](https://officialankan.github.io/sgu-client/api.html): every client method and model
- [Changelog](https://officialankan.github.io/sgu-client/about/changelog.html)

## Development

We recommend using [uv](https://github.com/astral-sh/uv) for development:

```bash
git clone https://github.com/officialankan/sgu-client.git
cd sgu-client
uv sync --all-groups --all-extras

uv run pytest
uv run ruff format
uv run ruff check --fix
uv run ty check
```

Contributions are welcome! Feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/officialankan/sgu-client/blob/main/LICENSE) file for details.

## Acknowledgments

- [Sveriges geologiska undersökning (SGU)](https://www.sgu.se/) for providing open access to groundwater data
- Built with [uv](https://github.com/astral-sh/uv), [Pydantic](https://pydantic.dev/), and [requests](https://requests.readthedocs.io/)
