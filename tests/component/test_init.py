"""Test component integration."""
import pytest
from unittest.mock import AsyncMock
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from custom_components.simple_device_creator import async_setup_entry


@pytest.mark.asyncio
async def test_async_setup_entry(hass: HomeAssistant, enable_custom_integrations):
    """Test setting up the integration."""
    # Create a config entry
    config_entry = ConfigEntry(
        entry_id="test_entry",
        domain="simple_device_creator",
        title="Simple Device Creator",
        data={"devices": []},
        source="user",
        options={},
        discovery_keys={},
        minor_version=1,
        subentries_data={},
        unique_id=None,
        version=1,
    )
    
    # Mock the async_forward_entry_setups since we have no platforms
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)
    
    assert await async_setup_entry(hass, config_entry)