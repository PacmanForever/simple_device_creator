"""Simple Device Creator integration for Home Assistant."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, PLATFORMS, CONF_NAME, CONF_MANUFACTURER, CONF_MODEL, CONF_SW_VERSION, CONF_HW_VERSION


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Simple Device Creator from a config entry."""
    # Store the config entry
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Register devices
    device_reg = dr.async_get(hass)
    devices = entry.data.get("devices", [])
    current_ids = set()

    for device_data in devices:
        device_id = device_data["id"]
        current_ids.add(device_id)
        
        # Check if device already exists in registry to accept name_by_user rename
        device_entry = device_reg.async_get_device(identifiers={(DOMAIN, device_id)})
        
        if device_entry and device_entry.name_by_user:
            # Sync Config Entry title and data if name_by_user is present
            if entry.title != device_entry.name_by_user:
                # Update data copy
                new_data = entry.data.copy()
                # Find the device in the new data to update it
                for dev in new_data.get("devices", []):
                    if dev["id"] == device_id:
                        dev[CONF_NAME] = device_entry.name_by_user
                        break
                
                hass.config_entries.async_update_entry(
                    entry, 
                    title=device_entry.name_by_user,
                    data=new_data
                )
                
                # Clear name_by_user from registry so the device uses the new integration name
                device_reg.async_update_device(device_entry.id, name_by_user=None)
                
                # Update local variable so async_get_or_create uses the new name
                device_data[CONF_NAME] = device_entry.name_by_user

        device_reg.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device_id)},
            name=device_data.get(CONF_NAME),
            manufacturer=device_data.get(CONF_MANUFACTURER),
            model=device_data.get(CONF_MODEL),
            sw_version=device_data.get(CONF_SW_VERSION),
            hw_version=device_data.get(CONF_HW_VERSION),
        )

    # Remove devices that are no longer in the config
    for device_entry in dr.async_entries_for_config_entry(device_reg, entry.entry_id):
        is_current = False
        for domain, identifier in device_entry.identifiers:
            if domain == DOMAIN and identifier in current_ids:
                is_current = True
                break
        
        if not is_current:
            device_reg.async_remove_device(device_entry.id)

    # Forward the setup to the platforms (none)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)



async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok