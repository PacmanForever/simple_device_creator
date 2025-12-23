"""Test init functions."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from custom_components.simple_device_creator import async_setup_entry, async_unload_entry


@pytest.mark.asyncio
async def test_async_setup_entry():
    """Test setting up the integration."""
    hass = MagicMock()
    hass.data = {}
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {"devices": []}

    # Mock async_forward_entry_setups
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch('custom_components.simple_device_creator.dr.async_get') as mock_async_get:
        device_reg = MagicMock()
        mock_async_get.return_value = device_reg

        result = await async_setup_entry(hass, entry)

    assert result is True
    assert entry.entry_id in hass.data["simple_device_creator"]
    device_reg.async_get_or_create.assert_not_called()  # No devices


@pytest.mark.asyncio
async def test_async_setup_entry_with_devices():
    """Test setting up with devices."""
    hass = MagicMock()
    hass.data = {}
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "devices": [
            {
                "id": "test_id",
                "name": "Test Device",
                "manufacturer": "Test Mfg",
                "model": "Test Model",
            }
        ]
    }

    # Mock async_forward_entry_setups
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch('custom_components.simple_device_creator.dr.async_get') as mock_async_get:
        device_reg = MagicMock()
        device_reg.async_get_or_create = AsyncMock()
        mock_async_get.return_value = device_reg

        result = await async_setup_entry(hass, entry)

    assert result is True
    device_reg.async_get_or_create.assert_called_once()


@pytest.mark.asyncio
async def test_async_unload_entry():
    """Test unloading the integration."""
    hass = MagicMock()
    hass.data = {"simple_device_creator": {"test_entry": "data"}}
    entry = MagicMock()
    entry.entry_id = "test_entry"
    
    # Mock async_unload_platforms
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    result = await async_unload_entry(hass, entry)

    assert result is True
    assert entry.entry_id not in hass.data["simple_device_creator"]