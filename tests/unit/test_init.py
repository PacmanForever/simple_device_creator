"""Test init functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.simple_device_creator import (
    async_migrate_entry,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.simple_device_creator.const import DOMAIN


@pytest.mark.asyncio
async def test_async_setup_entry_without_devices():
    """Test setting up the integration without devices."""
    hass = MagicMock()
    hass.data = {}
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {"devices": []}
    entry.version = 2
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch("custom_components.simple_device_creator.dr.async_get") as mock_async_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        mock_async_get.return_value = device_reg
        mock_entries.return_value = []

        result = await async_setup_entry(hass, entry)

    assert result is True
    device_reg.async_get_or_create.assert_not_called()


@pytest.mark.asyncio
async def test_async_setup_entry_with_multiple_devices():
    """Test setting up multiple devices in one entry."""
    hass = MagicMock()
    hass.data = {}
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "devices": [
            {"id": "device-1", "name": "Device 1", "manufacturer": "A"},
            {"id": "device-2", "name": "Device 2", "manufacturer": "B"},
        ]
    }
    entry.version = 2
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch("custom_components.simple_device_creator.dr.async_get") as mock_async_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        device_reg.async_get_or_create = MagicMock()
        device_reg.async_get_device.return_value = None
        mock_async_get.return_value = device_reg
        mock_entries.return_value = []

        result = await async_setup_entry(hass, entry)

    assert result is True
    assert device_reg.async_get_or_create.call_count == 2


@pytest.mark.asyncio
async def test_async_setup_entry_prunes_removed_devices():
    """Test pruning devices removed from the entry data."""
    hass = MagicMock()
    hass.data = {}
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {"devices": [{"id": "device-1", "name": "Device 1"}]}
    entry.version = 2
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch("custom_components.simple_device_creator.dr.async_get") as mock_async_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        device_reg.async_get_device.return_value = None
        mock_async_get.return_value = device_reg

        current_device = MagicMock()
        current_device.id = "current-device"
        current_device.identifiers = {(DOMAIN, "device-1")}

        old_device = MagicMock()
        old_device.id = "old-device"
        old_device.identifiers = {(DOMAIN, "old-device")}

        mock_entries.return_value = [current_device, old_device]

        result = await async_setup_entry(hass, entry)

    assert result is True
    device_reg.async_remove_device.assert_called_once_with("old-device")


@pytest.mark.asyncio
async def test_async_migrate_entry_consolidates_legacy_entries():
    """Test legacy single-device entries migrate into one General entry."""
    hass = MagicMock()

    primary_entry = MagicMock()
    primary_entry.entry_id = "entry-1"
    primary_entry.title = "Old One"
    primary_entry.data = {"devices": [{"id": "device-1", "name": "One"}]}
    primary_entry.version = 1

    secondary_entry = MagicMock()
    secondary_entry.entry_id = "entry-2"
    secondary_entry.title = "Old Two"
    secondary_entry.data = {"devices": [{"id": "device-2", "name": "Two"}]}
    secondary_entry.version = 1

    hass.config_entries.async_entries.return_value = [primary_entry, secondary_entry]
    hass.config_entries.async_remove = AsyncMock()

    result = await async_migrate_entry(hass, primary_entry)

    assert result is True
    hass.config_entries.async_update_entry.assert_called_once()
    call_kwargs = hass.config_entries.async_update_entry.call_args.kwargs
    assert call_kwargs["title"] == "General"
    assert len(call_kwargs["data"]["devices"]) == 2
    hass.config_entries.async_remove.assert_awaited_once_with("entry-2")


@pytest.mark.asyncio
async def test_async_migrate_entry_returns_true_for_current_version():
    """Test migration is a no-op for already current entries."""
    hass = MagicMock()
    entry = MagicMock()
    entry.version = 2

    result = await async_migrate_entry(hass, entry)

    assert result is True
    hass.config_entries.async_update_entry.assert_not_called()


@pytest.mark.asyncio
async def test_async_migrate_entry_without_async_entries_updates_current_entry():
    """Test migration falls back to updating the current entry when async_entries is unavailable."""
    hass = MagicMock()
    del hass.config_entries.async_entries
    entry = MagicMock()
    entry.version = 1

    result = await async_migrate_entry(hass, entry)

    assert result is True
    call_kwargs = hass.config_entries.async_update_entry.call_args.kwargs
    assert call_kwargs["title"] == "General"
    assert call_kwargs["version"] == 2


@pytest.mark.asyncio
async def test_async_migrate_entry_handles_no_legacy_entries():
    """Test migration updates version when no legacy entries are returned."""
    hass = MagicMock()
    entry = MagicMock()
    entry.version = 1
    hass.config_entries.async_entries.return_value = []

    result = await async_migrate_entry(hass, entry)

    assert result is True
    hass.config_entries.async_update_entry.assert_called_once_with(entry, version=2)


@pytest.mark.asyncio
async def test_async_migrate_entry_returns_false_for_secondary_legacy_entry():
    """Test secondary legacy entries do not become the migrated General entry."""
    hass = MagicMock()

    primary_entry = MagicMock()
    primary_entry.entry_id = "entry-1"
    primary_entry.title = "General"
    primary_entry.data = {"devices": [{"id": "device-1", "name": "One"}]}
    primary_entry.version = 1

    secondary_entry = MagicMock()
    secondary_entry.entry_id = "entry-2"
    secondary_entry.title = "Old Two"
    secondary_entry.data = {"devices": [{"id": "device-2", "name": "Two"}]}
    secondary_entry.version = 1

    hass.config_entries.async_entries.return_value = [primary_entry, secondary_entry]

    result = await async_migrate_entry(hass, secondary_entry)

    assert result is False


@pytest.mark.asyncio
async def test_async_migrate_entry_skips_missing_or_duplicate_device_ids():
    """Test migration ignores missing and duplicate legacy device IDs."""
    hass = MagicMock()

    primary_entry = MagicMock()
    primary_entry.entry_id = "entry-1"
    primary_entry.title = "General"
    primary_entry.data = {"devices": [{"id": "device-1", "name": "One"}, {"id": None, "name": "No ID"}]}
    primary_entry.version = 1

    secondary_entry = MagicMock()
    secondary_entry.entry_id = "entry-2"
    secondary_entry.title = "Old Two"
    secondary_entry.data = {"devices": [{"id": "device-1", "name": "Duplicate"}]}
    secondary_entry.version = 1

    hass.config_entries.async_entries.return_value = [primary_entry, secondary_entry]
    hass.config_entries.async_remove = AsyncMock()

    result = await async_migrate_entry(hass, primary_entry)

    assert result is True
    call_kwargs = hass.config_entries.async_update_entry.call_args.kwargs
    assert len(call_kwargs["data"]["devices"]) == 1


@pytest.mark.asyncio
async def test_async_unload_entry():
    """Test unloading the integration."""
    hass = MagicMock()
    hass.data = {"simple_device_creator": {"test_entry": "data"}}
    entry = MagicMock()
    entry.entry_id = "test_entry"
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