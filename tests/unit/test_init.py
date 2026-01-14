"""Test init functions."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from custom_components.simple_device_creator import async_setup_entry, async_unload_entry, async_reload_entry
from custom_components.simple_device_creator.const import DOMAIN


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

    with patch('custom_components.simple_device_creator.dr.async_get') as mock_async_get, \
         patch('custom_components.simple_device_creator.dr.async_entries_for_config_entry') as mock_entries:
        device_reg = MagicMock()
        mock_async_get.return_value = device_reg
        mock_entries.return_value = []

        result = await async_setup_entry(hass, entry)

    assert result is True
    assert entry.entry_id in hass.data["simple_device_creator"]
    device_reg.async_get_or_create.assert_not_called()  # No devices
    
    # Check update listener
    entry.add_update_listener.assert_called_once()
    entry.async_on_unload.assert_called_once()


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

    with patch('custom_components.simple_device_creator.dr.async_get') as mock_async_get, \
         patch('custom_components.simple_device_creator.dr.async_entries_for_config_entry') as mock_entries:
        device_reg = MagicMock()
        # device_reg.async_get_or_create is synchronous in real life, so MagicMock is correct.
        device_reg.async_get_or_create = MagicMock()
        mock_async_get.return_value = device_reg
        mock_entries.return_value = []

        result = await async_setup_entry(hass, entry)

    assert result is True
    device_reg.async_get_or_create.assert_called_once()
    
    # Check update listener
    entry.add_update_listener.assert_called_once()
    entry.async_on_unload.assert_called_once()


@pytest.mark.asyncio
async def test_async_setup_entry_prunes_devices():
    """Test pruning removed devices."""
    hass = MagicMock()
    hass.data = {}
    entry = MagicMock()
    entry.entry_id = "test_entry"
    # Current config has NO devices
    entry.data = {"devices": []}

    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch('custom_components.simple_device_creator.dr.async_get') as mock_async_get, \
         patch('custom_components.simple_device_creator.dr.async_entries_for_config_entry') as mock_entries:
        
        device_reg = MagicMock()
        mock_async_get.return_value = device_reg
        
        # Mock existing device in registry
        old_device = MagicMock()
        old_device.id = "old_device_reg_id"
        old_device.identifiers = {(DOMAIN, "old_device_id")}
        mock_entries.return_value = [old_device]

        result = await async_setup_entry(hass, entry)

    assert result is True
    # Verify old device was removed
    device_reg.async_remove_device.assert_called_once_with("old_device_reg_id")


@pytest.mark.asyncio
async def test_async_setup_entry_keeps_current_devices():
    """Test keeping current devices."""
    hass = MagicMock()
    hass.data = {}
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "devices": [
            {
                "id": "existing_device_id",
                "name": "Existing Device",
            }
        ]
    }

    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch('custom_components.simple_device_creator.dr.async_get') as mock_async_get, \
         patch('custom_components.simple_device_creator.dr.async_entries_for_config_entry') as mock_entries:
        
        device_reg = MagicMock()
        mock_async_get.return_value = device_reg
        
        # Mock existing device in registry
        existing_device = MagicMock()
        existing_device.id = "existing_device_reg_id"
        existing_device.identifiers = {(DOMAIN, "existing_device_id")}
        mock_entries.return_value = [existing_device]

        result = await async_setup_entry(hass, entry)

    assert result is True
    # Verify device was NOT removed
    device_reg.async_remove_device.assert_not_called()


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


@pytest.mark.asyncio
async def test_async_reload_entry():
    """Test reloading the integration."""
    hass = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry"
    
    hass.config_entries.async_reload = AsyncMock()

    await async_reload_entry(hass, entry)

    hass.config_entries.async_reload.assert_called_once_with(entry.entry_id)
