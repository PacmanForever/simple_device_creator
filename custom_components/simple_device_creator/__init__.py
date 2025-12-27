"""Simple Device Creator integration for Home Assistant."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, PLATFORMS, CONF_NAME, CONF_MANUFACTURER, CONF_MODEL, CONF_SW_VERSION, CONF_HW_VERSION, CONF_CONFIGURATION_URL, CONF_CONNECTIONS


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
            name=device_data.get(CONF_NAME),
            manufacturer=device_data.get(CONF_MANUFACTURER),
            model=device_data.get(CONF_MODEL),
            sw_version=device_data.get(CONF_SW_VERSION),
            hw_version=device_data.get(CONF_HW_VERSION),
            configuration_url=device_data.get(CONF_CONFIGURATION_URL),
            connections=set(tuple(conn) for conn in device_data.get(CONF_CONNECTIONS, [])),
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