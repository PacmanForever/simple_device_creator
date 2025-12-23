"""Test configuration and fixtures."""
import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations, request):
    """Enable custom integrations for component tests."""
    if "component" in str(request.fspath):
        enable_custom_integrations


@pytest.fixture
def hass():
    """Mock Home Assistant instance for unit tests."""
    return MagicMock()