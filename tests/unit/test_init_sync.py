"""Test init sync logic."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.simple_device_creator import async_setup_entry
from custom_components.simple_device_creator.const import CONF_NAME


@pytest.mark.asyncio
async def test_startup_sync_name_from_registry_updates_device_only():
    """Test that startup sync updates only the matching device name."""
    hass = MagicMock()
    hass.data = {}
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_update_entry = MagicMock()

    entry = MagicMock()
    entry.entry_id = "entry_123"
    entry.title = "Kitchen"
    entry.version = 2
    entry.data = {
        "devices": [
            {"id": "dev_123", CONF_NAME: "Old Name"},
            {"id": "dev_456", CONF_NAME: "Other Device"},
        ]
    }
    entry.async_on_unload = MagicMock()

    with patch("custom_components.simple_device_creator.dr.async_get") as mock_dr_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        mock_dr_get.return_value = device_reg

        renamed_device = MagicMock()
        renamed_device.id = "reg_dev_123"
        renamed_device.name_by_user = "New UI Name"

        def async_get_device_side_effect(*, identifiers):
            if identifiers == {("simple_device_creator", "dev_123")}:
                return renamed_device
            return None

        device_reg.async_get_device.side_effect = async_get_device_side_effect
        mock_entries.return_value = []

        await async_setup_entry(hass, entry)

    call_kwargs = hass.config_entries.async_update_entry.call_args.kwargs
    assert "title" not in call_kwargs
    assert call_kwargs["data"]["devices"][0][CONF_NAME] == "New UI Name"
    assert call_kwargs["data"]["devices"][1][CONF_NAME] == "Other Device"
    device_reg.async_update_device.assert_called_with("reg_dev_123", name_by_user=None)