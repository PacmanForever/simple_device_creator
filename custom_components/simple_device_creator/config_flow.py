"""Config flow for Simple Device Creator integration."""

import uuid

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_ENTRY_TITLE,
    CONF_HW_VERSION,
    CONF_MANUFACTURER,
    CONF_MODEL,
    CONF_NAME,
    CONF_SW_VERSION,
    DEFAULT_DEVICE_NAME,
    DEFAULT_ENTRY_TITLE,
    DEFAULT_HW_VERSION,
    DEFAULT_MANUFACTURER,
    DEFAULT_MODEL,
    DEFAULT_SW_VERSION,
    DOMAIN,
    MENU_ADD_DEVICE,
    MENU_DELETE_DEVICE,
    MENU_EDIT_DEVICE,
    MENU_FINISH,
    MENU_MOVE_DEVICE,
    MENU_RENAME_ENTRY,
)


CONF_DEVICE_ID = "device_id"
CONF_CONFIRM_DELETE = "confirm_delete"
CONF_TARGET_ENTRY_ID = "target_entry_id"


def _copy_devices(devices: list[dict]) -> list[dict]:
    """Copy stored device dictionaries."""
    return [device.copy() for device in devices]


def _build_device_schema(defaults: dict | None = None) -> vol.Schema:
    """Build the per-device form schema."""
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_DEVICE_NAME)): str,
            vol.Optional(
                CONF_MANUFACTURER,
                default=defaults.get(CONF_MANUFACTURER, DEFAULT_MANUFACTURER),
            ): str,
            vol.Optional(CONF_MODEL, default=defaults.get(CONF_MODEL, DEFAULT_MODEL)): str,
            vol.Optional(
                CONF_SW_VERSION,
                default=defaults.get(CONF_SW_VERSION, DEFAULT_SW_VERSION),
            ): str,
            vol.Optional(
                CONF_HW_VERSION,
                default=defaults.get(CONF_HW_VERSION, DEFAULT_HW_VERSION),
            ): str,
        }
    )


def _name_exists(devices: list[dict], name: str, excluded_id: str | None = None) -> bool:
    """Check whether a device name already exists inside the same entry."""
    normalized_name = name.strip().casefold()
    return any(
        device.get("id") != excluded_id
        and device.get(CONF_NAME, "").strip().casefold() == normalized_name
        for device in devices
    )


def _build_device_payload(user_input: dict, existing_id: str | None = None) -> dict:
    """Convert form input into the stored device payload."""
    return {
        "id": existing_id or str(uuid.uuid4()),
        CONF_NAME: user_input[CONF_NAME].strip(),
        CONF_MANUFACTURER: user_input[CONF_MANUFACTURER],
        CONF_MODEL: user_input[CONF_MODEL],
        CONF_SW_VERSION: user_input[CONF_SW_VERSION],
        CONF_HW_VERSION: user_input[CONF_HW_VERSION],
    }


class SimpleDeviceCreatorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Simple Device Creator."""

    VERSION = 2

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.entry_title = DEFAULT_ENTRY_TITLE
        self.devices: list[dict] = []

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Collect the entry title for the new device group."""
        if user_input is not None:
            self.entry_title = user_input[CONF_ENTRY_TITLE].strip() or DEFAULT_ENTRY_TITLE
            return await self.async_step_configure_devices()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_ENTRY_TITLE, default=self.entry_title): str}
            ),
        )

    async def async_step_add_device(self, user_input=None) -> FlowResult:
        """Add a device to the pending config entry."""
        errors = {}

        if user_input is not None:
            if _name_exists(self.devices, user_input[CONF_NAME]):
                errors["base"] = "name_already_exists"
            else:
                self.devices.append(_build_device_payload(user_input))
                return await self.async_step_configure_devices()

        return self.async_show_form(
            step_id="add_device",
            data_schema=_build_device_schema(),
            errors=errors,
        )

    async def async_step_configure_devices(self, user_input=None) -> FlowResult:
        """Offer actions after collecting at least one device."""
        return self.async_show_menu(
            step_id="configure_devices",
            menu_options=[MENU_ADD_DEVICE, MENU_FINISH],
        )

    async def async_step_finish(self, user_input=None) -> FlowResult:
        """Create the entry once devices are ready."""
        return self.async_create_entry(
            title=self.entry_title,
            data={"devices": self.devices},
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
        self.devices = _copy_devices(config_entry.data.get("devices", []))
        self._selected_device_id: str | None = None
        self._pending_action: str | None = None

    def _available_target_entries(self) -> list:
        """Return candidate destination entries for a move operation."""
        return [
            entry
            for entry in self.hass.config_entries.async_entries(DOMAIN)
            if entry.entry_id != self._config_entry.entry_id
        ]

    def _updated_entry_data(self) -> dict:
        """Build the updated config entry data payload."""
        return {**self._config_entry.data, "devices": self.devices}

    def _save_devices(self) -> None:
        """Persist the current device list to the config entry."""
        self.hass.config_entries.async_update_entry(
            self._config_entry,
            data=self._updated_entry_data(),
        )

    def _get_device(self, device_id: str | None = None) -> dict | None:
        """Return the matching stored device, if any."""
        target_id = device_id or self._selected_device_id
        if not target_id:
            return None

        for device in self.devices:
            if device["id"] == target_id:
                return device

        return None

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Show the main action menu."""
        menu_options = [MENU_ADD_DEVICE, MENU_RENAME_ENTRY]
        if self.devices:
            menu_options.extend([MENU_EDIT_DEVICE, MENU_DELETE_DEVICE])
            if self._available_target_entries():
                menu_options.append(MENU_MOVE_DEVICE)
        menu_options.append(MENU_FINISH)

        return self.async_show_menu(step_id="init", menu_options=menu_options)

    async def async_step_finish(self, user_input=None) -> FlowResult:
        """Finish the options flow."""
        return self.async_create_entry(title="", data={})

    async def async_step_rename_entry(self, user_input=None) -> FlowResult:
        """Rename the group entry."""
        if user_input is not None:
            entry_title = user_input[CONF_ENTRY_TITLE].strip() or DEFAULT_ENTRY_TITLE
            self.hass.config_entries.async_update_entry(
                self._config_entry,
                title=entry_title,
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="rename_entry",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ENTRY_TITLE,
                        default=self._config_entry.title or DEFAULT_ENTRY_TITLE,
                    ): str
                }
            ),
        )

    async def async_step_add_device(self, user_input=None) -> FlowResult:
        """Add a device to an existing group."""
        errors = {}

        if user_input is not None:
            if _name_exists(self.devices, user_input[CONF_NAME]):
                errors["base"] = "name_already_exists"
            else:
                self.devices.append(_build_device_payload(user_input))
                self._save_devices()
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="add_device",
            data_schema=_build_device_schema(),
            errors=errors,
        )

    async def async_step_select_device(self, user_input=None) -> FlowResult:
        """Select a device before editing or deleting it."""
        if not self.devices:
            return self.async_abort(reason="no_devices")

        if user_input is not None:
            self._selected_device_id = user_input[CONF_DEVICE_ID]
            if self._pending_action == MENU_EDIT_DEVICE:
                return await self.async_step_edit_device()
            if self._pending_action == MENU_DELETE_DEVICE:
                return await self.async_step_delete_device()
            if self._pending_action == MENU_MOVE_DEVICE:
                return await self.async_step_move_device()
            return await self.async_step_init()

        return self.async_show_form(
            step_id="select_device",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_ID): vol.In(
                        {device["id"]: device[CONF_NAME] for device in self.devices}
                    )
                }
            ),
        )

    async def async_step_edit_device(self, user_input=None) -> FlowResult:
        """Edit a stored device."""
        if self._selected_device_id is None:
            self._pending_action = MENU_EDIT_DEVICE
            return await self.async_step_select_device()

        device_data = self._get_device()
        if device_data is None:
            return self.async_abort(reason="device_not_found")

        registry = dr.async_get(self.hass)
        device_entry = registry.async_get_device(
            identifiers={(DOMAIN, device_data["id"])}
        )

        if user_input is not None:
            if _name_exists(self.devices, user_input[CONF_NAME], excluded_id=device_data["id"]):
                return self.async_show_form(
                    step_id="edit_device",
                    data_schema=_build_device_schema(user_input),
                    errors={"base": "name_already_exists"},
                )

            device_data.update(_build_device_payload(user_input, existing_id=device_data["id"]))
            self._save_devices()

            if device_entry:
                registry.async_update_device(device_entry.id, name_by_user=None)

            self._selected_device_id = None
            self._pending_action = None
            return self.async_create_entry(title="", data={})

        defaults = device_data.copy()
        if device_entry:
            defaults[CONF_NAME] = device_entry.name_by_user or device_entry.name or defaults[CONF_NAME]
            defaults[CONF_MANUFACTURER] = device_entry.manufacturer or defaults.get(CONF_MANUFACTURER, "")
            defaults[CONF_MODEL] = device_entry.model or defaults.get(CONF_MODEL, "")
            defaults[CONF_SW_VERSION] = device_entry.sw_version or defaults.get(CONF_SW_VERSION, "")
            defaults[CONF_HW_VERSION] = device_entry.hw_version or defaults.get(CONF_HW_VERSION, "")

        return self.async_show_form(
            step_id="edit_device",
            data_schema=_build_device_schema(defaults),
        )

    async def async_step_delete_device(self, user_input=None) -> FlowResult:
        """Delete a stored device from the entry."""
        if self._selected_device_id is None:
            self._pending_action = MENU_DELETE_DEVICE
            return await self.async_step_select_device()

        device_data = self._get_device()
        if device_data is None:
            return self.async_abort(reason="device_not_found")

        if user_input is not None:
            if user_input[CONF_CONFIRM_DELETE]:
                self.devices = [
                    device for device in self.devices if device["id"] != self._selected_device_id
                ]
                self._save_devices()

            self._selected_device_id = None
            self._pending_action = None
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="delete_device",
            data_schema=vol.Schema(
                {vol.Required(CONF_CONFIRM_DELETE, default=False): bool}
            ),
            description_placeholders={CONF_NAME: device_data[CONF_NAME]},
        )

    async def async_step_move_device(self, user_input=None) -> FlowResult:
        """Move a stored device to another hub."""
        if self._selected_device_id is None:
            self._pending_action = MENU_MOVE_DEVICE
            return await self.async_step_select_device()

        device_data = self._get_device()
        if device_data is None:
            return self.async_abort(reason="device_not_found")

        return await self.async_step_select_target_entry()

    async def async_step_select_target_entry(self, user_input=None) -> FlowResult:
        """Select the destination hub for the current device."""
        available_entries = self._available_target_entries()
        if not available_entries:
            return self.async_abort(reason="no_target_entries")

        device_data = self._get_device()
        if device_data is None:
            return self.async_abort(reason="device_not_found")

        errors = {}
        if user_input is not None:
            target_entry = next(
                (
                    entry
                    for entry in available_entries
                    if entry.entry_id == user_input[CONF_TARGET_ENTRY_ID]
                ),
                None,
            )
            if target_entry is None:
                return self.async_abort(reason="target_entry_not_found")

            target_devices = _copy_devices(target_entry.data.get("devices", []))
            if _name_exists(target_devices, device_data[CONF_NAME]):
                errors["base"] = "name_already_exists"
            else:
                target_devices.append(device_data.copy())
                self.hass.config_entries.async_update_entry(
                    target_entry,
                    data={**target_entry.data, "devices": target_devices},
                )

                registry = dr.async_get(self.hass)
                registry_device = registry.async_get_device(
                    identifiers={(DOMAIN, device_data["id"])}
                )
                registry.async_get_or_create(
                    config_entry_id=target_entry.entry_id,
                    identifiers={(DOMAIN, device_data["id"])},
                    name=device_data.get(CONF_NAME),
                    manufacturer=device_data.get(CONF_MANUFACTURER),
                    model=device_data.get(CONF_MODEL),
                    sw_version=device_data.get(CONF_SW_VERSION),
                    hw_version=device_data.get(CONF_HW_VERSION),
                )
                if registry_device:
                    registry.async_update_device(
                        registry_device.id,
                        remove_config_entry_id=self._config_entry.entry_id,
                    )

                self.devices = [
                    device
                    for device in self.devices
                    if device["id"] != self._selected_device_id
                ]
                self._save_devices()
                self._selected_device_id = None
                self._pending_action = None
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="select_target_entry",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_TARGET_ENTRY_ID): vol.In(
                        {
                            entry.entry_id: entry.title or entry.entry_id
                            for entry in available_entries
                        }
                    )
                }
            ),
            errors=errors,
            description_placeholders={CONF_NAME: device_data[CONF_NAME]},
        )