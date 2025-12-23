"""Test component integration."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from homeassistant.core import HomeAssistant
from custom_components.simple_device_creator import async_setup_entry


@pytest.mark.asyncio
async def test_async_setup_entry(hass: HomeAssistant, enable_custom_integrations):
    """Test setting up the integration."""
    # Create a mock config entry
    config_entry = MagicMock()
    config_entry.data = {"devices": []}
    config_entry.entry_id = "test_entry"
    
    # Mock the async_forward_entry_setups since we have no platforms
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)
    
    assert await async_setup_entry(hass, config_entry)