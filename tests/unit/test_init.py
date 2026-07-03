"""Test init functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import Event
from homeassistant.helpers import entity_registry as er

from custom_components.simple_device_creator import (
    _linked_entity_targets,
    _remove_entity_link,
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
         patch("custom_components.simple_device_creator.er.async_get") as mock_entity_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        mock_async_get.return_value = device_reg
        mock_entity_get.return_value = MagicMock()
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
         patch("custom_components.simple_device_creator.er.async_get") as mock_entity_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        device_reg.async_get_or_create = MagicMock()
        device_reg.async_get_device.return_value = None
        mock_async_get.return_value = device_reg
        mock_entity_get.return_value = MagicMock()
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
         patch("custom_components.simple_device_creator.er.async_get") as mock_entity_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        device_reg.async_get_device.return_value = None
        mock_async_get.return_value = device_reg
        mock_entity_get.return_value = MagicMock()

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
async def test_async_setup_entry_reapplies_linked_orphan_entities():
    """Test setup reattaches stored linked entities to the managed device."""
    hass = MagicMock()
    hass.data = {}
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "devices": [
            {"id": "device-1", "name": "Device 1", "entity_ids": ["sensor.orphan"]}
        ]
    }
    entry.version = 2
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch("custom_components.simple_device_creator.dr.async_get") as mock_device_get, \
         patch("custom_components.simple_device_creator.er.async_get") as mock_entity_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        registry_device = MagicMock()
        registry_device.id = "registry-device-id"
        registry_device.name_by_user = None
        device_reg.async_get_device.return_value = None
        device_reg.async_get_or_create.return_value = registry_device
        mock_device_get.return_value = device_reg

        entity_reg = MagicMock()
        entity_entry = MagicMock()
        entity_entry.device_id = None
        entity_reg.async_get.return_value = entity_entry
        mock_entity_get.return_value = entity_reg

        mock_entries.return_value = []

        result = await async_setup_entry(hass, entry)

    assert result is True
    entity_reg.async_update_entity.assert_called_once_with(
        "sensor.orphan", device_id="registry-device-id"
    )


@pytest.mark.asyncio
async def test_async_setup_entry_removes_missing_linked_entities_from_storage():
    """Test setup prunes stored linked entities that no longer exist."""
    hass = MagicMock()
    hass.data = {}
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "devices": [
            {"id": "device-1", "name": "Device 1", "entity_ids": ["sensor.missing"]}
        ]
    }
    entry.version = 2
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch("custom_components.simple_device_creator.dr.async_get") as mock_device_get, \
         patch("custom_components.simple_device_creator.er.async_get") as mock_entity_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        registry_device = MagicMock()
        registry_device.id = "registry-device-id"
        device_reg.async_get_device.return_value = None
        device_reg.async_get_or_create.return_value = registry_device
        mock_device_get.return_value = device_reg

        entity_reg = MagicMock()
        entity_reg.async_get.return_value = None
        mock_entity_get.return_value = entity_reg
        mock_entries.return_value = []

        result = await async_setup_entry(hass, entry)

    assert result is True
    call_kwargs = hass.config_entries.async_update_entry.call_args.kwargs
    assert call_kwargs["data"]["devices"][0]["entity_ids"] == []
    assert hass.data[DOMAIN][entry.entry_id]["devices"][0]["entity_ids"] == []


@pytest.mark.asyncio
async def test_async_setup_entry_entity_listener_removes_deleted_link_from_storage():
    """Test entity registry remove events prune stored linked entities."""
    hass = MagicMock()
    hass.data = {}
    hass.bus.async_listen = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "devices": [
            {"id": "device-1", "name": "Device 1", "entity_ids": ["sensor.orphan"]}
        ]
    }
    entry.version = 2
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch("custom_components.simple_device_creator.dr.async_get") as mock_device_get, \
         patch("custom_components.simple_device_creator.er.async_get") as mock_entity_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        registry_device = MagicMock()
        registry_device.id = "registry-device-id"
        device_reg.async_get_device.return_value = None
        device_reg.async_get_or_create.return_value = registry_device
        mock_device_get.return_value = device_reg

        entity_reg = MagicMock()
        entity_entry = MagicMock()
        entity_entry.device_id = "registry-device-id"
        entity_reg.async_get.return_value = entity_entry
        mock_entity_get.return_value = entity_reg
        mock_entries.return_value = []

        await async_setup_entry(hass, entry)

    entity_listener = None
    for call in hass.bus.async_listen.call_args_list:
        args, _ = call
        if args[0] == er.EVENT_ENTITY_REGISTRY_UPDATED:
            entity_listener = args[1]
            break

    assert entity_listener is not None
    entity_listener(Event(er.EVENT_ENTITY_REGISTRY_UPDATED, {"action": "remove", "entity_id": "sensor.orphan"}))

    call_kwargs = hass.config_entries.async_update_entry.call_args.kwargs
    assert call_kwargs["data"]["devices"][0]["entity_ids"] == []


@pytest.mark.asyncio
async def test_async_setup_entry_entity_listener_reapplies_target_device_on_update():
    """Test entity registry update events reassign stored linked entities back to the target device."""
    hass = MagicMock()
    hass.data = {}
    hass.bus.async_listen = MagicMock()
    entry = MagicMock()
    entry.entry_id = "test_entry"
    entry.data = {
        "devices": [
            {"id": "device-1", "name": "Device 1", "entity_ids": ["sensor.orphan"]}
        ]
    }
    entry.version = 2
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=None)

    with patch("custom_components.simple_device_creator.dr.async_get") as mock_device_get, \
         patch("custom_components.simple_device_creator.er.async_get") as mock_entity_get, \
         patch("custom_components.simple_device_creator.dr.async_entries_for_config_entry") as mock_entries:
        device_reg = MagicMock()
        initial_registry_device = MagicMock()
        initial_registry_device.id = "registry-device-id"
        target_device = MagicMock()
        target_device.id = "registry-device-id"
        device_reg.async_get_device.side_effect = [None, target_device]
        device_reg.async_get_or_create.return_value = initial_registry_device
        mock_device_get.return_value = device_reg

        entity_reg = MagicMock()
        entity_entry = MagicMock()
        entity_entry.device_id = "wrong-device-id"
        entity_reg.async_get.return_value = entity_entry
        mock_entity_get.return_value = entity_reg
        mock_entries.return_value = []

        await async_setup_entry(hass, entry)

    entity_listener = None
    for call in hass.bus.async_listen.call_args_list:
        args, _ = call
        if args[0] == er.EVENT_ENTITY_REGISTRY_UPDATED:
            entity_listener = args[1]
            break

    assert entity_listener is not None
    entity_reg.async_update_entity.reset_mock()

    entity_listener(Event(er.EVENT_ENTITY_REGISTRY_UPDATED, {"action": "update", "entity_id": "sensor.orphan"}))

    entity_reg.async_update_entity.assert_called_once_with(
        "sensor.orphan", device_id="registry-device-id"
    )


def test_remove_entity_link_helper_removes_only_matching_entity():
    """Test helper removes only the requested linked entity."""
    data = {
        "devices": [
            {"id": "device-1", "entity_ids": ["sensor.one", "sensor.two"]},
            {"id": "device-2", "entity_ids": ["sensor.three"]},
        ]
    }

    changed = _remove_entity_link(data, "sensor.two")

    assert changed is True
    assert data["devices"][0]["entity_ids"] == ["sensor.one"]
    assert data["devices"][1]["entity_ids"] == ["sensor.three"]


def test_linked_entity_targets_helper_ignores_devices_without_ids():
    """Test helper maps linked entities to internal device IDs and skips invalid devices."""
    data = {
        "devices": [
            {"id": "device-1", "entity_ids": ["sensor.one", "sensor.two"]},
            {"entity_ids": ["sensor.skip"]},
            {"id": "device-2", "entity_ids": []},
        ]
    }

    targets = _linked_entity_targets(data)

    assert targets == {"sensor.one": "device-1", "sensor.two": "device-1"}


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