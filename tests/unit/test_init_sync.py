"""Test init sync logic."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.helpers import device_registry as dr
from custom_components.simple_device_creator import async_setup_entry
from custom_components.simple_device_creator.const import DOMAIN, CONF_NAME

@pytest.mark.asyncio
async def test_startup_sync_name_from_registry():
    """Test that startup syncs the config entry title from registry name_by_user."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_update_entry = MagicMock()
    
    entry = MagicMock()
    entry.entry_id = "entry_123"
    entry.title = "Old Name"
    entry.data = {
        "devices": [
            {
                "id": "dev_123",
                CONF_NAME: "Old Name"
            }
        ]
    }
    entry.async_on_unload = MagicMock()

    # Mock Registry
    with patch('custom_components.simple_device_creator.dr.async_get') as mock_dr_get,          patch('custom_components.simple_device_creator.dr.async_entries_for_config_entry') as mock_entries:
        
        device_reg = MagicMock()
        mock_dr_get.return_value = device_reg
        
        # Scenario: Device exists in registry with a User Override Name
        mock_device = MagicMock()
        mock_device.id = "reg_dev_123"
        mock_device.name_by_user = "New UI Name"
        
        # When looking up by identifiers
        device_reg.async_get_device.return_value = mock_device
        
        # When creating
        device_reg.async_get_or_create.return_value = mock_device

        mock_entries.return_value = []

        await async_setup_entry(hass, entry)
        
        # Checks
        # 1. Verification that update_entry was called to sync the title
        # It should update both Title and Data["name"]
        
        assert hass.config_entries.async_update_entry.called
        call_args = hass.config_entries.async_update_entry.call_args[1]
        assert call_args["title"] == "New UI Name"
        
        # We also want to ensure the internal data is updated so it persists properly
        # Note: entry.data is usually immutable in real HA, so we rely on async_update_entry(data=...)
        assert "data" in call_args
        assert call_args["data"]["devices"][0][CONF_NAME] == "New UI Name"

        # 2. We should optionally clear name_by_user to canonize the name, 
        # BUT wait - if we do that, we are modifying the user's intent?
        # If we update the config entry to match, then the integration name becomes "New UI Name".
        # If we clear name_by_user, the device falls back to integration name.
        # This keeps it clean.
        device_reg.async_update_device.assert_called_with(mock_device.id, name_by_user=None)

