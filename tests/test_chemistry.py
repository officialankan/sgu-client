"""Simple smoke test for chemistry module to verify basic functionality."""

from sgu_client import SGUClient


def test_chemistry_client_exists():
    """Test that chemistry client is accessible."""
    client = SGUClient()
    assert hasattr(client, "chemistry")
    assert hasattr(client.chemistry, "get_sampling_sites")
    assert hasattr(client.chemistry, "get_analysis_results")


def test_chemistry_models_importable():
    """Test that chemistry models can be imported."""
    from sgu_client.models.chemistry import (
        AnalysisResult,
        AnalysisResultCollection,
        SamplingSite,
        SamplingSiteCollection,
    )

    assert AnalysisResult is not None
    assert AnalysisResultCollection is not None
    assert SamplingSite is not None
    assert SamplingSiteCollection is not None
