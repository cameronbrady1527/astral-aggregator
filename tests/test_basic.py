# ==============================================================================
# test_basic.py — Basic Test to Verify Test Setup
# ==============================================================================
# Purpose: Simple test to ensure pytest and test infrastructure works
# ==============================================================================

import pytest


def test_basic_functionality():
    """Basic test to verify pytest is working."""
    assert True
    assert 1 + 1 == 2
    assert "hello" in "hello world"


def test_string_operations():
    """Test basic string operations."""
    text = "aggregator"
    assert len(text) == 10
    assert text.upper() == "AGGREGATOR"
    assert text.startswith("agg")


@pytest.mark.unit
def test_unit_marker():
    """Test that unit markers work."""
    assert True


@pytest.mark.slow
def test_slow_marker():
    """Test that slow markers work."""
    assert True


class TestBasicClass:
    """Basic test class to verify class-based tests work."""
    
    def test_class_method(self):
        """Test method within a class."""
        assert True
    
    def test_with_fixture(self, sample_site_config):
        """Test using a fixture."""
        assert sample_site_config is not None
        assert "name" in sample_site_config
        assert sample_site_config["name"] == "Test Site" 