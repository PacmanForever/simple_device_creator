"""Test device rename syncing."""
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from homeassistant.core import Event
from homeassistant.helpers import device_registry as dr
from custom_components.simple_device_creator import async_setup_entry
from custom_components.simple_device_creator.const import DOMAIN, CONF_NAME

@pytest.mark.asyncio
async def test_device_rename_sync_listener():
    """Test that renaming a device triggers config entry update."""
    hass = MagicMock()
    hass.data = {}
    hass.bus.async_listen = MagicMock()
    
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.title = "Old Name"
    # MappingProxyType simulation for entry.data
    entry.data = {
        "devices": [
            {
                "id": "device_123",
                CONF_NAME: "Old Name",
            }
        ]
    }
    
    # Mock config_entries methods
    hass.config_entries.async_update_entry = MagicMock()
    hass.config_entries.async_reload = AsyncMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    with patch('custom_components.simple_device_creator.dr.async_get') as mock_async_get, \
         patch('custom_components.simple_device_creator.dr.async_entries_for_config_entry') as mock_entries:
        
        device_reg = MagicMock()
        mock_async_get.return_value = device_reg
        mock_entries.return_value = []
        
        # Setup the entry
        await async_setup_entry(hass, entry)
        
        # Verify listener registration
        # Since using hass.bus.async_listen, we check that
        assert hass.bus.async_listen.called
        
        # Find the listener for EVENT_DEVICE_REGISTRY_UPDATED
        listener_callback = None
        for call in hass.bus.async_listen.call_args_list:
            args, _ = call
            if args[0] == dr.EVENT_DEVICE_REGISTRY_UPDATED:
                listener_callback = args[1]
                break
        
        assert listener_callback is not None
        
        # Simulate an event: User renames device in registry
        event_data = {
            "action": "update",
            "device_id": "reg_device_id"
        }
        event = Event(dr.EVENT_DEVICE_REGISTRY_UPDATED, event_data)
        
        # Mock device lookup for the listener
        device_entry = MagicMock()
        device_entry.id = "reg_device_id"
        device_entry.identifiers = {(DOMAIN, "device_123")}
        device_entry.config_entries = {"test_entry"}
        device_entry.name_by_user = "New Name"
        
        device_reg.async_get.return_value = device_entry
        
        # Call the listener
        listener_callback(event)
        
        # Check if async_update_entry was called with new title
        assert hass.config_entries.async_update_entry.called
        call_args = hass.config_entries.async_update_entry.call_args
        # call_args[0] is (entry, )
        # call_args[1] is kwargs {title: ..., data: ...}
        assert call_args[1]["title"] == "New Name"
        assert call_args[1]["data"]["devices"][0][CONF_NAME] == "New Name"
        
        # Check if async_update_device was called to clear name_by_user
        device_reg.async_update_device.assert_called_with("reg_device_id", name_by_user=None)
