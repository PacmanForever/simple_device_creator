"""Test device rename syncing."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import Event
from homeassistant.helpers import device_registry as dr

from custom_components.simple_device_creator import async_setup_entry
from custom_components.simple_device_creator.const import CONF_NAME, DOMAIN


async def _setup_entry_and_get_listener():
    """Set up the integration and return the registered device listener."""
    hass = MagicMock()
    hass.data = {}
    hass.bus.async_listen = MagicMock()

    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.title = "General"
    entry.version = 2
    entry.data = {
        "devices": [
            {"id": "device_123", CONF_NAME: "Device 123"},
            {"id": "device_456", CONF_NAME: "Device 456"},
        ]
    }

    hass.config_entries.async_update_entry = MagicMock()
    hass.config_entries.async_reload = AsyncMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    with patch("custom_components.simple_device_creator.dr.async_get") as mock_async_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        mock_async_get.return_value = device_reg
        device_reg.async_get_device.return_value = None
        mock_entries.return_value = []

        await async_setup_entry(hass, entry)

    listener_callback = None
    for call in hass.bus.async_listen.call_args_list:
        args, _ = call
        if args[0] == dr.EVENT_DEVICE_REGISTRY_UPDATED:
            listener_callback = args[1]
            break

    assert listener_callback is not None
    return hass, entry, device_reg, listener_callback


@pytest.mark.asyncio
async def test_device_rename_sync_listener_updates_only_matching_device():
    """Test that renaming a device updates only that device in stored data."""
    hass, _entry, device_reg, listener_callback = await _setup_entry_and_get_listener()

    event = Event(
        dr.EVENT_DEVICE_REGISTRY_UPDATED,
        {"action": "update", "device_id": "reg_device_id"},
    )

    device_entry = MagicMock()
    device_entry.id = "reg_device_id"
    device_entry.identifiers = {(DOMAIN, "device_456")}
    device_entry.config_entries = {"test_entry"}
    device_entry.name_by_user = "Renamed Device"

    device_reg.async_get.return_value = device_entry

    listener_callback(event)

    call_kwargs = hass.config_entries.async_update_entry.call_args.kwargs
    assert "title" not in call_kwargs
    assert call_kwargs["data"]["devices"][0][CONF_NAME] == "Device 123"
    assert call_kwargs["data"]["devices"][1][CONF_NAME] == "Renamed Device"
    device_reg.async_update_device.assert_called_with("reg_device_id", name_by_user=None)


@pytest.mark.asyncio
async def test_device_rename_listener_ignores_irrelevant_events():
    """Test that listener ignores invalid or unrelated registry events."""
    hass, _entry, device_reg, listener_callback = await _setup_entry_and_get_listener()

    listener_callback(Event(dr.EVENT_DEVICE_REGISTRY_UPDATED, {"action": "create"}))
    listener_callback(Event(dr.EVENT_DEVICE_REGISTRY_UPDATED, {"action": "update"}))

    device_reg.async_get.return_value = None
    listener_callback(
        Event(dr.EVENT_DEVICE_REGISTRY_UPDATED, {"action": "update", "device_id": "reg_device_id"})
    )

    unrelated_device = MagicMock()
    unrelated_device.config_entries = {"another_entry"}
    unrelated_device.name_by_user = "Other Name"
    device_reg.async_get.return_value = unrelated_device
    listener_callback(
        Event(dr.EVENT_DEVICE_REGISTRY_UPDATED, {"action": "update", "device_id": "reg_device_id"})
    )

    hass.config_entries.async_update_entry.assert_not_called()
    device_reg.async_update_device.assert_not_called()


@pytest.mark.asyncio
async def test_device_rename_listener_ignores_missing_internal_identifier():
    """Test that listener ignores registry devices without integration identifiers."""
    hass, _entry, device_reg, listener_callback = await _setup_entry_and_get_listener()

    device_entry = MagicMock()
    device_entry.id = "reg_device_id"
    device_entry.identifiers = {("other_domain", "device_123")}
    device_entry.config_entries = {"test_entry"}
    device_entry.name_by_user = "New Name"

    device_reg.async_get.return_value = device_entry

    listener_callback(
        Event(dr.EVENT_DEVICE_REGISTRY_UPDATED, {"action": "update", "device_id": "reg_device_id"})
    )

    hass.config_entries.async_update_entry.assert_not_called()
    device_reg.async_update_device.assert_not_called()


@pytest.mark.asyncio
async def test_device_rename_listener_ignores_updates_without_name_by_user():
    """Test that listener ignores updates when the registry entry has no user rename."""
    hass, _entry, device_reg, listener_callback = await _setup_entry_and_get_listener()

    device_entry = MagicMock()
    device_entry.id = "reg_device_id"
    device_entry.identifiers = {(DOMAIN, "device_456")}
    device_entry.config_entries = {"test_entry"}
    device_entry.name_by_user = None

    device_reg.async_get.return_value = device_entry

    listener_callback(
        Event(dr.EVENT_DEVICE_REGISTRY_UPDATED, {"action": "update", "device_id": "reg_device_id"})
    )

    hass.config_entries.async_update_entry.assert_not_called()
    device_reg.async_update_device.assert_not_called()