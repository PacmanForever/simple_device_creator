"""Simple Device Creator integration for Home Assistant."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, PLATFORMS


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Simple Device Creator from a config entry."""
    # Store the config entry
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Register devices
    device_reg = dr.async_get(hass)
    devices = entry.data.get("devices", [])
    for device_data in devices:
        device_reg.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device_data["id"])},
            name=device_data.get("name"),
            manufacturer=device_data.get("manufacturer"),
            model=device_data.get("model"),
            sw_version=device_data.get("sw_version"),
            hw_version=device_data.get("hw_version"),
            configuration_url=device_data.get("configuration_url"),
            connections=set(tuple(conn) for conn in device_data.get("connections", [])),
        )

    # Forward the setup to the platforms (none)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok