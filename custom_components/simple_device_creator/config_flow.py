"""Config flow for Simple Device Creator integration."""
import uuid
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_CONFIGURATION_URL,
    CONF_CONNECTIONS,
    CONF_HW_VERSION,
    CONF_MANUFACTURER,
    CONF_MODEL,
    CONF_NAME,
    CONF_SW_VERSION,
    DEFAULT_CONFIGURATION_URL,
    DEFAULT_DEVICE_NAME,
    DEFAULT_HW_VERSION,
    DEFAULT_MANUFACTURER,
    DEFAULT_MODEL,
    DEFAULT_SW_VERSION,
    DOMAIN,
    MENU_CREATE_DEVICE,
    MENU_DELETE_DEVICE,
    MENU_EDIT_DEVICE,
    MENU_FINISH,
    MENU_OPTIONS,
)


def parse_connections(connections_str):
    """Parse connections string to list of tuples."""
    connections = []
    if not connections_str:
        return connections
        
    for conn in connections_str.split(","):
        conn = conn.strip()
        if not conn:
            continue
        if ":" not in conn:
            raise ValueError("invalid_format")
        conn_type, conn_value = conn.split(":", 1)
        connections.append((conn_type.strip(), conn_value.strip()))
    return connections


class SimpleDeviceCreatorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Simple Device Creator."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.devices = []

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            if user_input["menu_option"] == MENU_FINISH:
                return self.async_create_entry(
                    title="Simple Device Creator",
                    data={"devices": self.devices},
                )
            elif user_input["menu_option"] == MENU_CREATE_DEVICE:
                return await self.async_step_create_device()
            elif user_input["menu_option"] == MENU_EDIT_DEVICE:
                return await self.async_step_select_device()
            elif user_input["menu_option"] == MENU_DELETE_DEVICE:
                return await self.async_step_select_device(delete=True)

        menu_options = MENU_OPTIONS

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("menu_option"): vol.In(menu_options),
                }
            ),
            description_placeholders={
                "device_count": len(self.devices),
            },
        )

    async def async_step_create_device(self, user_input=None) -> FlowResult:
        """Handle device creation."""

        if user_input is not None:
            # Validate name uniqueness
            if any(d[CONF_NAME] == user_input[CONF_NAME] for d in self.devices):
                return self.async_show_form(
                    step_id="create_device",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_NAME, default=DEFAULT_DEVICE_NAME): str,
                            vol.Optional(CONF_MANUFACTURER, default=DEFAULT_MANUFACTURER): str,
                            vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): str,
                            vol.Optional(CONF_SW_VERSION, default=DEFAULT_SW_VERSION): str,
                            vol.Optional(CONF_HW_VERSION, default=DEFAULT_HW_VERSION): str,
                            vol.Optional(CONF_CONFIGURATION_URL, default=DEFAULT_CONFIGURATION_URL): str,
                            vol.Optional(CONF_CONNECTIONS, default=""): str,
                        }
                    ),
                    description_placeholders={
                        "help_connections": "Format: type1:value1, type2:value2 (e.g., mac:AA:BB:CC:DD:EE:FF, ip:192.168.1.1)"
                    },
                    errors={"name": "name_already_exists"},
                )

            # Parse and validate connections
            try:
                connections = parse_connections(user_input.get(CONF_CONNECTIONS))
            except ValueError:
                return self.async_show_form(
                    step_id="create_device",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_NAME, default=user_input[CONF_NAME]): str,
                            vol.Optional(CONF_MANUFACTURER, default=user_input[CONF_MANUFACTURER]): str,
                            vol.Optional(CONF_MODEL, default=user_input[CONF_MODEL]): str,
                            vol.Optional(CONF_SW_VERSION, default=user_input[CONF_SW_VERSION]): str,
                            vol.Optional(CONF_HW_VERSION, default=user_input[CONF_HW_VERSION]): str,
                            vol.Optional(CONF_CONFIGURATION_URL, default=user_input[CONF_CONFIGURATION_URL]): str,
                            vol.Optional(CONF_CONNECTIONS, default=user_input[CONF_CONNECTIONS]): str,
                        }
                    ),
                    description_placeholders={
                        "help_connections": "Format: type1:value1, type2:value2 (e.g., mac:AA:BB:CC:DD:EE:FF, ip:192.168.1.1)"
                    },
                    errors={"connections": "invalid_format"},
                )

            device = {
                "id": str(uuid.uuid4()),
                CONF_NAME: user_input[CONF_NAME],
                CONF_MANUFACTURER: user_input[CONF_MANUFACTURER],
                CONF_MODEL: user_input[CONF_MODEL],
                CONF_SW_VERSION: user_input[CONF_SW_VERSION],
                CONF_HW_VERSION: user_input[CONF_HW_VERSION],
                CONF_CONFIGURATION_URL: user_input[CONF_CONFIGURATION_URL],
                CONF_CONNECTIONS: connections,
            }
            self.devices.append(device)
            return await self.async_step_user()

        return self.async_show_form(
            step_id="create_device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_DEVICE_NAME): str,
                    vol.Optional(CONF_MANUFACTURER, default=DEFAULT_MANUFACTURER): str,
                    vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): str,
                    vol.Optional(CONF_SW_VERSION, default=DEFAULT_SW_VERSION): str,
                    vol.Optional(CONF_HW_VERSION, default=DEFAULT_HW_VERSION): str,
                    vol.Optional(CONF_CONFIGURATION_URL, default=DEFAULT_CONFIGURATION_URL): str,
                    vol.Optional(CONF_CONNECTIONS, default=""): str,
                }
            ),
            description_placeholders={
                "help_connections": "Format: type1:value1, type2:value2 (e.g., mac:AA:BB:CC:DD:EE:FF, ip:192.168.1.1)"
            },
        )

    async def async_step_select_device(self, user_input=None, delete=False) -> FlowResult:
        """Select a device to edit or delete."""
        if not self.devices:
            return await self.async_step_user()

        if user_input is not None:
            device_id = user_input["device_id"]
            if delete:
                self.devices = [d for d in self.devices if d["id"] != device_id]
                return await self.async_step_user()
            else:
                self.selected_device_id = device_id
                return await self.async_step_edit_device()

        device_options = {d["id"]: d[CONF_NAME] for d in self.devices}

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {
                    vol.Required("device_id"): vol.In(device_options),
                }
            ),
            description_placeholders={
                "action": "delete" if delete else "edit",
            },
        )

    async def async_step_edit_device(self, user_input=None) -> FlowResult:
        """Edit an existing device."""
        device = next(d for d in self.devices if d["id"] == self.selected_device_id)

        if user_input is not None:
            # Validate name uniqueness
            if any(d[CONF_NAME] == user_input[CONF_NAME] and d["id"] != self.selected_device_id for d in self.devices):
                connections_str = ", ".join(f"{t}:{v}" for t, v in device.get(CONF_CONNECTIONS, []))
                return self.async_show_form(
                    step_id="edit_device",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_NAME, default=device[CONF_NAME]): str,
                            vol.Optional(CONF_MANUFACTURER, default=device.get(CONF_MANUFACTURER, "")): str,
                            vol.Optional(CONF_MODEL, default=device.get(CONF_MODEL, "")): str,
                            vol.Optional(CONF_SW_VERSION, default=device.get(CONF_SW_VERSION, "")): str,
                            vol.Optional(CONF_HW_VERSION, default=device.get(CONF_HW_VERSION, "")): str,
                            vol.Optional(CONF_CONFIGURATION_URL, default=device.get(CONF_CONFIGURATION_URL, "")): str,
                            vol.Optional(CONF_CONNECTIONS, default=connections_str): str,
                        }
                    ),
                    description_placeholders={
                        "help_connections": "Format: type1:value1, type2:value2"
                    },
                    errors={"name": "name_already_exists"},
                )

            # Parse and validate connections
            try:
                connections = parse_connections(user_input.get(CONF_CONNECTIONS))
            except ValueError:
                return self.async_show_form(
                    step_id="edit_device",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_NAME, default=user_input[CONF_NAME]): str,
                            vol.Optional(CONF_MANUFACTURER, default=user_input[CONF_MANUFACTURER]): str,
                            vol.Optional(CONF_MODEL, default=user_input[CONF_MODEL]): str,
                            vol.Optional(CONF_SW_VERSION, default=user_input[CONF_SW_VERSION]): str,
                            vol.Optional(CONF_HW_VERSION, default=user_input[CONF_HW_VERSION]): str,
                            vol.Optional(CONF_CONFIGURATION_URL, default=user_input[CONF_CONFIGURATION_URL]): str,
                            vol.Optional(CONF_CONNECTIONS, default=user_input[CONF_CONNECTIONS]): str,
                        }
                    ),
                    description_placeholders={
                        "help_connections": "Format: type1:value1, type2:value2"
                    },
                    errors={"connections": "invalid_format"},
                )

            device.update({
                CONF_NAME: user_input[CONF_NAME],
                CONF_MANUFACTURER: user_input[CONF_MANUFACTURER],
                CONF_MODEL: user_input[CONF_MODEL],
                CONF_SW_VERSION: user_input[CONF_SW_VERSION],
                CONF_HW_VERSION: user_input[CONF_HW_VERSION],
                CONF_CONFIGURATION_URL: user_input[CONF_CONFIGURATION_URL],
                CONF_CONNECTIONS: connections,
            })
            return await self.async_step_user()

        connections_str = ", ".join(f"{t}:{v}" for t, v in device.get(CONF_CONNECTIONS, []))

        return self.async_show_form(
            step_id="edit_device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=device[CONF_NAME]): str,
                    vol.Optional(CONF_MANUFACTURER, default=device.get(CONF_MANUFACTURER, "")): str,
                    vol.Optional(CONF_MODEL, default=device.get(CONF_MODEL, "")): str,
                    vol.Optional(CONF_SW_VERSION, default=device.get(CONF_SW_VERSION, "")): str,
                    vol.Optional(CONF_HW_VERSION, default=device.get(CONF_HW_VERSION, "")): str,
                    vol.Optional(CONF_CONFIGURATION_URL, default=device.get(CONF_CONFIGURATION_URL, "")): str,
                    vol.Optional(CONF_CONNECTIONS, default=connections_str): str,
                }
            ),
            description_placeholders={
                "help_connections": "Format: type1:value1, type2:value2"
            },
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
        if user_input is not None:
            if user_input["menu_option"] == MENU_FINISH:
                return self.async_create_entry(
                    title="",
                    data={"devices": self.devices},
                )
            elif user_input["menu_option"] == MENU_CREATE_DEVICE:
                return await self.async_step_create_device()
            elif user_input["menu_option"] == MENU_EDIT_DEVICE:
                return await self.async_step_select_device()
            elif user_input["menu_option"] == MENU_DELETE_DEVICE:
                return await self.async_step_select_device(delete=True)

        menu_options = MENU_OPTIONS

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("menu_option"): vol.In(menu_options),
                }
            ),
            description_placeholders={
                "device_count": len(self.devices),
            },
        )

    async def async_step_create_device(self, user_input=None) -> FlowResult:
        """Handle device creation in options."""
        # Same as config flow

        if user_input is not None:
            # Validate name uniqueness
            if any(d[CONF_NAME] == user_input[CONF_NAME] for d in self.devices):
                return self.async_show_form(
                    step_id="create_device",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_NAME, default=DEFAULT_DEVICE_NAME): str,
                            vol.Optional(CONF_MANUFACTURER, default=DEFAULT_MANUFACTURER): str,
                            vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): str,
                            vol.Optional(CONF_SW_VERSION, default=DEFAULT_SW_VERSION): str,
                            vol.Optional(CONF_HW_VERSION, default=DEFAULT_HW_VERSION): str,
                            vol.Optional(CONF_CONFIGURATION_URL, default=DEFAULT_CONFIGURATION_URL): str,
                            vol.Optional(CONF_CONNECTIONS, default=""): str,
                        }
                    ),
                    description_placeholders={
                        "help_connections": "Format: type1:value1, type2:value2"
                    },
                    errors={"name": "name_already_exists"},
                )

            # Parse and validate connections
            try:
                connections = parse_connections(user_input.get(CONF_CONNECTIONS))
            except ValueError:
                return self.async_show_form(
                    step_id="create_device",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_NAME, default=user_input[CONF_NAME]): str,
                            vol.Optional(CONF_MANUFACTURER, default=user_input[CONF_MANUFACTURER]): str,
                            vol.Optional(CONF_MODEL, default=user_input[CONF_MODEL]): str,
                            vol.Optional(CONF_SW_VERSION, default=user_input[CONF_SW_VERSION]): str,
                            vol.Optional(CONF_HW_VERSION, default=user_input[CONF_HW_VERSION]): str,
                            vol.Optional(CONF_CONFIGURATION_URL, default=user_input[CONF_CONFIGURATION_URL]): str,
                            vol.Optional(CONF_CONNECTIONS, default=user_input[CONF_CONNECTIONS]): str,
                        }
                    ),
                    description_placeholders={
                        "help_connections": "Format: type1:value1, type2:value2"
                    },
                    errors={"connections": "invalid_format"},
                )

            device = {
                "id": str(uuid.uuid4()),
                CONF_NAME: user_input[CONF_NAME],
                CONF_MANUFACTURER: user_input[CONF_MANUFACTURER],
                CONF_MODEL: user_input[CONF_MODEL],
                CONF_SW_VERSION: user_input[CONF_SW_VERSION],
                CONF_HW_VERSION: user_input[CONF_HW_VERSION],
                CONF_CONFIGURATION_URL: user_input[CONF_CONFIGURATION_URL],
                CONF_CONNECTIONS: connections,
            }
            self.devices.append(device)
            return await self.async_step_user()

        return self.async_show_form(
            step_id="create_device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_DEVICE_NAME): str,
                    vol.Optional(CONF_MANUFACTURER, default=DEFAULT_MANUFACTURER): str,
                    vol.Optional(CONF_MODEL, default=DEFAULT_MODEL): str,
                    vol.Optional(CONF_SW_VERSION, default=DEFAULT_SW_VERSION): str,
                    vol.Optional(CONF_HW_VERSION, default=DEFAULT_HW_VERSION): str,
                    vol.Optional(CONF_CONFIGURATION_URL, default=DEFAULT_CONFIGURATION_URL): str,
                    vol.Optional(CONF_CONNECTIONS, default=""): str,
                }
            ),
            description_placeholders={
                "help_connections": "Format: type1:value1, type2:value2"
            },
        )

    async def async_step_select_device(self, user_input=None, delete=False) -> FlowResult:
        """Select a device to edit or delete in options."""
        if not self.devices:
            return await self.async_step_user()

        if user_input is not None:
            device_id = user_input["device_id"]
            if delete:
                self.devices = [d for d in self.devices if d["id"] != device_id]
                return await self.async_step_user()
            else:
                self.selected_device_id = device_id
                return await self.async_step_edit_device()

        device_options = {d["id"]: d[CONF_NAME] for d in self.devices}

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {
                    vol.Required("device_id"): vol.In(device_options),
                }
            ),
            description_placeholders={
                "action": "delete" if delete else "edit",
            },
        )

    async def async_step_edit_device(self, user_input=None) -> FlowResult:
        """Edit an existing device in options."""
        device = next(d for d in self.devices if d["id"] == self.selected_device_id)

        if user_input is not None:
            # Validate name uniqueness
            if any(d[CONF_NAME] == user_input[CONF_NAME] and d["id"] != self.selected_device_id for d in self.devices):
                connections_str = ", ".join(f"{t}:{v}" for t, v in device.get(CONF_CONNECTIONS, []))
                return self.async_show_form(
                    step_id="edit_device",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_NAME, default=device[CONF_NAME]): str,
                            vol.Optional(CONF_MANUFACTURER, default=device.get(CONF_MANUFACTURER, "")): str,
                            vol.Optional(CONF_MODEL, default=device.get(CONF_MODEL, "")): str,
                            vol.Optional(CONF_SW_VERSION, default=device.get(CONF_SW_VERSION, "")): str,
                            vol.Optional(CONF_HW_VERSION, default=device.get(CONF_HW_VERSION, "")): str,
                            vol.Optional(CONF_CONFIGURATION_URL, default=device.get(CONF_CONFIGURATION_URL, "")): str,
                            vol.Optional(CONF_CONNECTIONS, default=connections_str): str,
                        }
                    ),
                    description_placeholders={
                        "help_connections": "Format: type1:value1, type2:value2"
                    },
                    errors={"name": "name_already_exists"},
                )

            # Parse and validate connections
            try:
                connections = parse_connections(user_input.get(CONF_CONNECTIONS))
            except ValueError:
                return self.async_show_form(
                    step_id="edit_device",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_NAME, default=user_input[CONF_NAME]): str,
                            vol.Optional(CONF_MANUFACTURER, default=user_input[CONF_MANUFACTURER]): str,
                            vol.Optional(CONF_MODEL, default=user_input[CONF_MODEL]): str,
                            vol.Optional(CONF_SW_VERSION, default=user_input[CONF_SW_VERSION]): str,
                            vol.Optional(CONF_HW_VERSION, default=user_input[CONF_HW_VERSION]): str,
                            vol.Optional(CONF_CONFIGURATION_URL, default=user_input[CONF_CONFIGURATION_URL]): str,
                            vol.Optional(CONF_CONNECTIONS, default=user_input[CONF_CONNECTIONS]): str,
                        }
                    ),
                    description_placeholders={
                        "help_connections": "Format: type1:value1, type2:value2"
                    },
                    errors={"connections": "invalid_format"},
                )

            device.update({
                CONF_NAME: user_input[CONF_NAME],
                CONF_MANUFACTURER: user_input[CONF_MANUFACTURER],
                CONF_MODEL: user_input[CONF_MODEL],
                CONF_SW_VERSION: user_input[CONF_SW_VERSION],
                CONF_HW_VERSION: user_input[CONF_HW_VERSION],
                CONF_CONFIGURATION_URL: user_input[CONF_CONFIGURATION_URL],
                CONF_CONNECTIONS: connections,
            })
            return await self.async_step_user()

        connections_str = ", ".join(f"{t}:{v}" for t, v in device.get(CONF_CONNECTIONS, []))

        return self.async_show_form(
            step_id="edit_device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=device[CONF_NAME]): str,
                    vol.Optional(CONF_MANUFACTURER, default=device.get(CONF_MANUFACTURER, "")): str,
                    vol.Optional(CONF_MODEL, default=device.get(CONF_MODEL, "")): str,
                    vol.Optional(CONF_SW_VERSION, default=device.get(CONF_SW_VERSION, "")): str,
                    vol.Optional(CONF_HW_VERSION, default=device.get(CONF_HW_VERSION, "")): str,
                    vol.Optional(CONF_CONFIGURATION_URL, default=device.get(CONF_CONFIGURATION_URL, "")): str,
                    vol.Optional(CONF_CONNECTIONS, default=connections_str): str,
                }
            ),
            description_placeholders={
                "help_connections": "Format: type1:value1, type2:value2"
            },
        )