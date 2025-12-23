"""Test constants."""
from custom_components.simple_device_creator.const import DOMAIN


def test_domain():
    """Test that DOMAIN is correct."""
    assert DOMAIN == "simple_device_creator"