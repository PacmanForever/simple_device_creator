"""Config flow for Simple Device Creator integration."""
import uuid
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_HW_VERSION,
    CONF_MANUFACTURER,
    CONF_MODEL,
    CONF_NAME,
    CONF_SW_VERSION,
    DEFAULT_DEVICE_NAME,
    DEFAULT_HW_VERSION,
    DEFAULT_MANUFACTURER,
    DEFAULT_MODEL,
    DEFAULT_SW_VERSION,
    DOMAIN,
)


class SimpleDeviceCreatorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Simple Device Creator."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.devices = []

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            if not errors:
                device = {
                    "id": str(uuid.uuid4()),
                    CONF_NAME: user_input[CONF_NAME],
                    CONF_MANUFACTURER: user_input[CONF_MANUFACTURER],
                    CONF_MODEL: user_input[CONF_MODEL],
                    CONF_SW_VERSION: user_input[CONF_SW_VERSION],
                    CONF_HW_VERSION: user_input[CONF_HW_VERSION],
                }
                
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={"devices": [device]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_DEVICE_NAME): str,
                    vol.Optional(CONF_MANUFACTURER, default=DEFAULT_MANUFACTURER): str,
                    vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): str,
                    vol.Optional(CONF_SW_VERSION, default=DEFAULT_SW_VERSION): str,
                    vol.Optional(CONF_HW_VERSION, default=DEFAULT_HW_VERSION): str,
                }
            ),
            description_placeholders={
            },
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SimpleDeviceCreatorOptionsFlow(config_entry)


class SimpleDeviceCreatorOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Simple Device Creator."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self._config_entry = config_entry
        self.devices = config_entry.data.get("devices", [])

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the options step."""
        # Use the first device
        if not self.devices:
             return self.async_create_entry(title="", data={"devices": []})
        
        device_data = self.devices[0]
        
        # Get Device Registry to sync names
        registry = dr.async_get(self.hass)
        device_entry = registry.async_get_device(identifiers={(DOMAIN, device_data["id"])})

        if user_input is not None:
            # Update internal config
            device_data.update({
                CONF_NAME: user_input[CONF_NAME],
                CONF_MANUFACTURER: user_input[CONF_MANUFACTURER],
                CONF_MODEL: user_input[CONF_MODEL],
                CONF_SW_VERSION: user_input[CONF_SW_VERSION],
                CONF_HW_VERSION: user_input[CONF_HW_VERSION],
            })

            # Sync with device registry if it exists
            if device_entry:
                # Clear name_by_user so the new integration name takes precedence (via reload)
                registry.async_update_device(device_entry.id, name_by_user=None)

            # Update config entry title
            self.hass.config_entries.async_update_entry(
                self._config_entry, title=user_input[CONF_NAME]
            )

            return self.async_create_entry(title="", data={"devices": self.devices})

        # Pre-fill defaults
        default_name = device_data[CONF_NAME]
        default_manufacturer = device_data.get(CONF_MANUFACTURER, "")
        default_model = device_data.get(CONF_MODEL, "")
        default_sw = device_data.get(CONF_SW_VERSION, "")
        default_hw = device_data.get(CONF_HW_VERSION, "")

        if device_entry:
            default_name = device_entry.name_by_user or device_entry.name or default_name
            # Also sync other fields if available in registry
            default_manufacturer = device_entry.manufacturer or default_manufacturer
            default_model = device_entry.model or default_model
            default_sw = device_entry.sw_version or default_sw
            default_hw = device_entry.hw_version or default_hw

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=default_name): str,
                    vol.Optional(CONF_MANUFACTURER, default=default_manufacturer): str,
                    vol.Optional(CONF_MODEL, default=default_model): str,
                    vol.Optional(CONF_SW_VERSION, default=default_sw): str,
                    vol.Optional(CONF_HW_VERSION, default=default_hw): str,
                }
            ),
            description_placeholders={
            },
        )


    # Removed async_step_create_device, async_step_select_device, async_step_edit_device
