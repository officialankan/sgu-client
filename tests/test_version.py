"""Test version consistency across project files."""

import tomllib
from pathlib import Path

import sgu_client


def test_version_consistency():
    """Test that pyproject.toml and __init__.py have matching versions."""
    # Get project root directory
    project_root = Path(__file__).parent.parent

    # Read version from pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    pyproject_version = pyproject_data["project"]["version"]

    # Get version from __init__.py
    init_version = sgu_client.__version__

    # Assert they match
    assert pyproject_version == init_version, (
        f"Version mismatch: pyproject.toml has '{pyproject_version}' "
        f"but __init__.py has '{init_version}'"
    )
