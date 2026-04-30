"""Simple Device Creator integration for Home Assistant."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_HW_VERSION,
    CONF_MANUFACTURER,
    CONF_MODEL,
    CONF_NAME,
    CONF_SW_VERSION,
    DEFAULT_ENTRY_TITLE,
    DOMAIN,
    PLATFORMS,
)

CURRENT_ENTRY_VERSION = 2


def _copy_entry_data(entry_data: dict) -> dict:
    """Copy entry data while preserving nested device dictionaries."""
    copied_data = dict(entry_data)
    copied_data["devices"] = [device.copy() for device in entry_data.get("devices", [])]
    return copied_data


def _find_internal_device_id(device_entry) -> str | None:
    """Extract the integration-owned device identifier from the registry entry."""
    for domain, identifier in device_entry.identifiers:
        if domain == DOMAIN:
            return identifier
    return None


def _entry_version(entry: ConfigEntry) -> int:
    """Return the entry version, defaulting to the current version for tests/mocks."""
    version = getattr(entry, "version", CURRENT_ENTRY_VERSION)
    return version if isinstance(version, int) else CURRENT_ENTRY_VERSION


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate legacy single-device entries into one General entry."""
    if _entry_version(entry) >= CURRENT_ENTRY_VERSION:
        return True

    async_entries = getattr(hass.config_entries, "async_entries", None)
    if not callable(async_entries):
        hass.config_entries.async_update_entry(
            entry,
            title=DEFAULT_ENTRY_TITLE,
            version=CURRENT_ENTRY_VERSION,
        )
        return True

    all_entries = list(async_entries(DOMAIN))
    legacy_entries = [
        existing for existing in all_entries if _entry_version(existing) < CURRENT_ENTRY_VERSION
    ]
    if not legacy_entries:
        hass.config_entries.async_update_entry(entry, version=CURRENT_ENTRY_VERSION)
        return True

    general_entry = next(
        (existing for existing in legacy_entries if existing.title == DEFAULT_ENTRY_TITLE),
        entry,
    )
    if entry.entry_id != general_entry.entry_id:
        return False

    merged_devices = []
    seen_ids = set()
    for legacy_entry in legacy_entries:
        for device_data in legacy_entry.data.get("devices", []):
            device_id = device_data.get("id")
            if not device_id or device_id in seen_ids:
                continue
            merged_devices.append(device_data.copy())
            seen_ids.add(device_id)

    hass.config_entries.async_update_entry(
        general_entry,
        title=DEFAULT_ENTRY_TITLE,
        data={"devices": merged_devices},
        version=CURRENT_ENTRY_VERSION,
    )

    async_remove = getattr(hass.config_entries, "async_remove", None)
    if callable(async_remove):
        for legacy_entry in legacy_entries:
            if legacy_entry.entry_id == general_entry.entry_id:
                continue
            await async_remove(legacy_entry.entry_id)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Simple Device Creator from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    device_reg = dr.async_get(hass)
    new_data = _copy_entry_data(entry.data)
    devices = new_data.get("devices", [])
    current_ids = set()
    data_changed = False

    for device_data in devices:
        device_id = device_data["id"]
        current_ids.add(device_id)

        device_entry = device_reg.async_get_device(identifiers={(DOMAIN, device_id)})
        if device_entry and device_entry.name_by_user:
            if device_data.get(CONF_NAME) != device_entry.name_by_user:
                device_data[CONF_NAME] = device_entry.name_by_user
                data_changed = True
            device_reg.async_update_device(device_entry.id, name_by_user=None)

        device_reg.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device_id)},
            name=device_data.get(CONF_NAME),
            manufacturer=device_data.get(CONF_MANUFACTURER),
            model=device_data.get(CONF_MODEL),
            sw_version=device_data.get(CONF_SW_VERSION),
            hw_version=device_data.get(CONF_HW_VERSION),
        )

    if data_changed:
        hass.config_entries.async_update_entry(entry, data=new_data)
        hass.data[DOMAIN][entry.entry_id] = new_data

    for device_entry in dr.async_entries_for_config_entry(device_reg, entry.entry_id):
        internal_device_id = _find_internal_device_id(device_entry)
        if internal_device_id not in current_ids:
            device_reg.async_remove_device(device_entry.id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    @callback
    def async_registry_updated(event: Event) -> None:
        """Handle device registry updates."""
        if event.data["action"] != "update":
            return
        if "device_id" not in event.data:
            return

        registry_device = device_reg.async_get(event.data["device_id"])
        if not registry_device:
            return
        if entry.entry_id not in registry_device.config_entries:
            return
        if not registry_device.name_by_user:
            return

        internal_device_id = _find_internal_device_id(registry_device)
        if not internal_device_id:
            return

        updated_data = _copy_entry_data(entry.data)
        for device_data in updated_data.get("devices", []):
            if device_data["id"] != internal_device_id:
                continue

            if device_data.get(CONF_NAME) != registry_device.name_by_user:
                device_data[CONF_NAME] = registry_device.name_by_user
                hass.config_entries.async_update_entry(entry, data=updated_data)

            device_reg.async_update_device(registry_device.id, name_by_user=None)
            return

    entry.async_on_unload(
        hass.bus.async_listen(dr.EVENT_DEVICE_REGISTRY_UPDATED, async_registry_updated)
    )
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok