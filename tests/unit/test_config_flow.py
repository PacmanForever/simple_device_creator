"""Test config and options flows."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.simple_device_creator.config_flow import (
    CONF_CONFIRM_DELETE,
    CONF_DEVICE_ID,
    CONF_TARGET_ENTRY_ID,
    SimpleDeviceCreatorConfigFlow,
    SimpleDeviceCreatorOptionsFlow,
)
from custom_components.simple_device_creator.const import (
    CONF_ENTRY_TITLE,
    CONF_HW_VERSION,
    CONF_MANUFACTURER,
    CONF_MODEL,
    CONF_NAME,
    CONF_SW_VERSION,
    DEFAULT_ENTRY_TITLE,
    DOMAIN,
)


class TestSimpleDeviceCreatorConfigFlow:
    """Test the config flow."""

    def test_init(self):
        """Test initialization."""
        flow = SimpleDeviceCreatorConfigFlow()
        assert flow.devices == []
        assert flow.entry_title == DEFAULT_ENTRY_TITLE

    @pytest.mark.asyncio
    async def test_step_user_show_form(self):
        """Test user step shows the group name form."""
        flow = SimpleDeviceCreatorConfigFlow()

        result = await flow.async_step_user()

        assert result["type"] == "form"
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_step_user_moves_to_add_device(self):
        """Test submitting the group name moves to group configuration."""
        flow = SimpleDeviceCreatorConfigFlow()

        result = await flow.async_step_user({CONF_ENTRY_TITLE: "Kitchen"})

        assert result["type"] == "menu"
        assert result["step_id"] == "configure_devices"
        assert flow.entry_title == "Kitchen"

    @pytest.mark.asyncio
    async def test_add_device_and_finish_creates_entry(self):
        """Test creating a group entry after adding a device."""
        flow = SimpleDeviceCreatorConfigFlow()
        await flow.async_step_user({CONF_ENTRY_TITLE: "Kitchen"})

        result = await flow.async_step_add_device(
            {
                CONF_NAME: "Test Device",
                CONF_MANUFACTURER: "Test Manufacturer",
                CONF_MODEL: "Test Model",
                CONF_SW_VERSION: "1.0.0",
                CONF_HW_VERSION: "1.0",
            }
        )

        assert result["type"] == "menu"
        assert result["step_id"] == "configure_devices"

        result = await flow.async_step_finish()

        assert result["type"] == "create_entry"
        assert result["title"] == "Kitchen"
        assert len(result["data"]["devices"]) == 1
        assert result["data"]["devices"][0][CONF_NAME] == "Test Device"

    @pytest.mark.asyncio
    async def test_add_device_rejects_duplicate_names(self):
        """Test duplicate device names are rejected within a group."""
        flow = SimpleDeviceCreatorConfigFlow()
        await flow.async_step_user({CONF_ENTRY_TITLE: "Kitchen"})

        first_device = {
            CONF_NAME: "Repeated",
            CONF_MANUFACTURER: "Maker",
            CONF_MODEL: "Model",
            CONF_SW_VERSION: "1.0",
            CONF_HW_VERSION: "1.0",
        }
        await flow.async_step_add_device(first_device)

        result = await flow.async_step_add_device(first_device)

        assert result["type"] == "form"
        assert result["errors"]["base"] == "name_already_exists"

    @pytest.mark.asyncio
    async def test_finish_without_devices_creates_empty_entry(self):
        """Test finishing without devices creates an empty group entry."""
        flow = SimpleDeviceCreatorConfigFlow()
        flow.entry_title = "Kitchen"

        result = await flow.async_step_finish()

        assert result["type"] == "create_entry"
        assert result["title"] == "Kitchen"
        assert result["data"]["devices"] == []

    def test_async_get_options_flow(self):
        """Test get options flow."""
        config_entry = MagicMock()
        flow = SimpleDeviceCreatorConfigFlow.async_get_options_flow(config_entry)
        assert isinstance(flow, SimpleDeviceCreatorOptionsFlow)


class TestSimpleDeviceCreatorOptionsFlow:
    """Test the options flow."""

    def _build_flow(self, devices=None, title="General"):
        config_entry = MagicMock()
        config_entry.entry_id = f"entry-{title}"
        config_entry.title = title
        config_entry.data = {"devices": devices or []}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        flow.hass = MagicMock()
        flow.hass.config_entries.async_entries.return_value = [config_entry]
        return flow, config_entry

    @pytest.mark.asyncio
    async def test_step_init_shows_menu(self):
        """Test init step shows the options menu."""
        flow, _config_entry = self._build_flow(
            devices=[{"id": "dev-1", CONF_NAME: "Device 1"}]
        )

        result = await flow.async_step_init()

        assert result["type"] == "menu"
        assert result["step_id"] == "init"
        assert "add_device" in result["menu_options"]
        assert "rename_entry" in result["menu_options"]

    @pytest.mark.asyncio
    async def test_step_init_includes_move_when_other_hub_exists(self):
        """Test init step includes move when another hub exists."""
        flow, config_entry = self._build_flow(devices=[{"id": "dev-1", CONF_NAME: "Device 1"}])
        other_entry = MagicMock()
        other_entry.entry_id = "entry-other"
        other_entry.title = "Other"
        other_entry.data = {"devices": []}
        flow.hass.config_entries.async_entries.return_value = [config_entry, other_entry]

        result = await flow.async_step_init()

        assert "move_device" in result["menu_options"]

    @pytest.mark.asyncio
    async def test_rename_entry_updates_title(self):
        """Test renaming the group entry."""
        flow, config_entry = self._build_flow()

        result = await flow.async_step_rename_entry({CONF_ENTRY_TITLE: "Living Room"})

        assert result["type"] == "create_entry"
        flow.hass.config_entries.async_update_entry.assert_called_once_with(
            config_entry,
            title="Living Room",
        )

    @pytest.mark.asyncio
    async def test_rename_entry_shows_form(self):
        """Test rename entry shows the form when no input is provided."""
        flow, _config_entry = self._build_flow(title="Kitchen")

        result = await flow.async_step_rename_entry()

        assert result["type"] == "form"
        assert result["step_id"] == "rename_entry"

    @pytest.mark.asyncio
    async def test_add_device_updates_entry_data(self):
        """Test adding a device updates config entry data."""
        flow, config_entry = self._build_flow(title="Kitchen")

        result = await flow.async_step_add_device(
            {
                CONF_NAME: "Sensor",
                CONF_MANUFACTURER: "Maker",
                CONF_MODEL: "Model",
                CONF_SW_VERSION: "1.0",
                CONF_HW_VERSION: "1.0",
            }
        )

        assert result["type"] == "create_entry"
        call_kwargs = flow.hass.config_entries.async_update_entry.call_args.kwargs
        assert call_kwargs["data"]["devices"][0][CONF_NAME] == "Sensor"
        assert config_entry.data == {"devices": []}

    @pytest.mark.asyncio
    async def test_add_device_shows_form_and_rejects_duplicate(self):
        """Test add device form display and duplicate-name rejection."""
        flow, _config_entry = self._build_flow(devices=[{"id": "dev-1", CONF_NAME: "Sensor"}])

        result = await flow.async_step_add_device()
        assert result["type"] == "form"
        assert result["step_id"] == "add_device"

        duplicate_result = await flow.async_step_add_device(
            {
                CONF_NAME: "Sensor",
                CONF_MANUFACTURER: "Maker",
                CONF_MODEL: "Model",
                CONF_SW_VERSION: "1.0",
                CONF_HW_VERSION: "1.0",
            }
        )

        assert duplicate_result["errors"]["base"] == "name_already_exists"

    @pytest.mark.asyncio
    async def test_finish_options_flow_creates_empty_result(self):
        """Test finish step closes the options flow."""
        flow, _config_entry = self._build_flow()

        result = await flow.async_step_finish()

        assert result["type"] == "create_entry"

    def test_get_device_without_selection_returns_none(self):
        """Test the helper returns None when no device is selected."""
        flow, _config_entry = self._build_flow()

        assert flow._get_device() is None

    @pytest.mark.asyncio
    async def test_select_device_without_devices_aborts(self):
        """Test select device aborts when no devices exist."""
        flow, _config_entry = self._build_flow()

        result = await flow.async_step_select_device()

        assert result["type"] == "abort"
        assert result["reason"] == "no_devices"

    @pytest.mark.asyncio
    async def test_select_device_shows_form(self):
        """Test select device displays the selection form."""
        flow, _config_entry = self._build_flow(devices=[{"id": "dev-1", CONF_NAME: "Device 1"}])

        result = await flow.async_step_select_device()

        assert result["type"] == "form"
        assert result["step_id"] == "select_device"

    @pytest.mark.asyncio
    async def test_select_device_routes_to_edit_and_delete(self):
        """Test select device routes to the pending action."""
        flow, _config_entry = self._build_flow(
            devices=[
                {"id": "dev-1", CONF_NAME: "Device 1", CONF_MANUFACTURER: "A", CONF_MODEL: "M1", CONF_SW_VERSION: "1", CONF_HW_VERSION: "1"},
                {"id": "dev-2", CONF_NAME: "Device 2", CONF_MANUFACTURER: "B", CONF_MODEL: "M2", CONF_SW_VERSION: "2", CONF_HW_VERSION: "2"},
            ]
        )

        flow._pending_action = "edit_device"
        with patch("custom_components.simple_device_creator.config_flow.dr.async_get") as mock_dr_get:
            mock_registry = MagicMock()
            mock_dr_get.return_value = mock_registry
            mock_registry.async_get_device.return_value = None
            edit_result = await flow.async_step_select_device({CONF_DEVICE_ID: "dev-1"})

        assert edit_result["type"] == "form"
        assert edit_result["step_id"] == "edit_device"

        flow._pending_action = "delete_device"
        flow._selected_device_id = None
        delete_result = await flow.async_step_select_device({CONF_DEVICE_ID: "dev-2"})
        assert delete_result["type"] == "form"
        assert delete_result["step_id"] == "delete_device"

        other_entry = MagicMock()
        other_entry.entry_id = "entry-other"
        other_entry.title = "Other"
        other_entry.data = {"devices": []}
        flow.hass.config_entries.async_entries.return_value = [_config_entry, other_entry]
        flow._pending_action = "move_device"
        flow._selected_device_id = None
        move_result = await flow.async_step_select_device({CONF_DEVICE_ID: "dev-1"})
        assert move_result["type"] == "form"
        assert move_result["step_id"] == "select_target_entry"

    @pytest.mark.asyncio
    async def test_edit_device_without_selected_device_uses_selector(self):
        """Test edit device goes through selection when no device is selected."""
        flow, _config_entry = self._build_flow(devices=[{"id": "dev-1", CONF_NAME: "Device 1"}])

        result = await flow.async_step_edit_device()

        assert result["type"] == "form"
        assert result["step_id"] == "select_device"

    @pytest.mark.asyncio
    async def test_edit_device_missing_selected_device_aborts(self):
        """Test edit device aborts when the selected device no longer exists."""
        flow, _config_entry = self._build_flow(devices=[{"id": "dev-1", CONF_NAME: "Device 1"}])
        flow._selected_device_id = "missing"

        result = await flow.async_step_edit_device()

        assert result["type"] == "abort"
        assert result["reason"] == "device_not_found"

    @pytest.mark.asyncio
    async def test_edit_device_duplicate_name_rejected(self):
        """Test editing a device rejects duplicate names within the group."""
        flow, _config_entry = self._build_flow(
            devices=[
                {"id": "dev-1", CONF_NAME: "Device 1", CONF_MANUFACTURER: "A", CONF_MODEL: "M1", CONF_SW_VERSION: "1", CONF_HW_VERSION: "1"},
                {"id": "dev-2", CONF_NAME: "Device 2", CONF_MANUFACTURER: "B", CONF_MODEL: "M2", CONF_SW_VERSION: "2", CONF_HW_VERSION: "2"},
            ]
        )
        flow._selected_device_id = "dev-2"

        with patch("custom_components.simple_device_creator.config_flow.dr.async_get") as mock_dr_get:
            mock_registry = MagicMock()
            mock_dr_get.return_value = mock_registry
            mock_registry.async_get_device.return_value = None

            result = await flow.async_step_edit_device(
                {
                    CONF_NAME: "Device 1",
                    CONF_MANUFACTURER: "B",
                    CONF_MODEL: "M2",
                    CONF_SW_VERSION: "2",
                    CONF_HW_VERSION: "2",
                }
            )

        assert result["type"] == "form"
        assert result["errors"]["base"] == "name_already_exists"

    @pytest.mark.asyncio
    async def test_edit_device_form_prefills_registry_values(self):
        """Test edit device form prefers registry values when available."""
        flow, _config_entry = self._build_flow(
            devices=[{"id": "dev-1", CONF_NAME: "Device 1", CONF_MANUFACTURER: "A", CONF_MODEL: "M1", CONF_SW_VERSION: "1", CONF_HW_VERSION: "1"}]
        )
        flow._selected_device_id = "dev-1"

        with patch("custom_components.simple_device_creator.config_flow.dr.async_get") as mock_dr_get:
            mock_registry = MagicMock()
            mock_dr_get.return_value = mock_registry
            registry_device = MagicMock()
            registry_device.name_by_user = "Registry Name"
            registry_device.name = "Fallback"
            registry_device.manufacturer = "Registry Maker"
            registry_device.model = "Registry Model"
            registry_device.sw_version = "9"
            registry_device.hw_version = "8"
            mock_registry.async_get_device.return_value = registry_device

            result = await flow.async_step_edit_device()

        assert result["type"] == "form"
        assert result["step_id"] == "edit_device"

    @pytest.mark.asyncio
    async def test_delete_device_without_selected_device_uses_selector(self):
        """Test delete device goes through selection when no device is selected."""
        flow, _config_entry = self._build_flow(
            devices=[{"id": "dev-1", CONF_NAME: "Device 1"}, {"id": "dev-2", CONF_NAME: "Device 2"}]
        )

        result = await flow.async_step_delete_device()

        assert result["type"] == "form"
        assert result["step_id"] == "select_device"

    @pytest.mark.asyncio
    async def test_delete_device_missing_selected_device_aborts(self):
        """Test delete device aborts when the selected device no longer exists."""
        flow, _config_entry = self._build_flow(
            devices=[{"id": "dev-1", CONF_NAME: "Device 1"}, {"id": "dev-2", CONF_NAME: "Device 2"}]
        )
        flow._selected_device_id = "missing"

        result = await flow.async_step_delete_device()

        assert result["type"] == "abort"
        assert result["reason"] == "device_not_found"

    @pytest.mark.asyncio
    async def test_delete_device_shows_confirmation_form(self):
        """Test delete device shows confirmation before removal."""
        flow, _config_entry = self._build_flow(
            devices=[{"id": "dev-1", CONF_NAME: "Device 1"}, {"id": "dev-2", CONF_NAME: "Device 2"}]
        )
        flow._selected_device_id = "dev-2"

        result = await flow.async_step_delete_device()

        assert result["type"] == "form"
        assert result["step_id"] == "delete_device"

    @pytest.mark.asyncio
    async def test_edit_device_updates_matching_device(self):
        """Test editing a selected device updates only that device."""
        flow, config_entry = self._build_flow(
            devices=[
                {"id": "dev-1", CONF_NAME: "Device 1", CONF_MANUFACTURER: "A", CONF_MODEL: "M1", CONF_SW_VERSION: "1", CONF_HW_VERSION: "1"},
                {"id": "dev-2", CONF_NAME: "Device 2", CONF_MANUFACTURER: "B", CONF_MODEL: "M2", CONF_SW_VERSION: "2", CONF_HW_VERSION: "2"},
            ]
        )

        with patch("custom_components.simple_device_creator.config_flow.dr.async_get") as mock_dr_get:
            mock_registry = MagicMock()
            mock_dr_get.return_value = mock_registry
            mock_device = MagicMock()
            mock_device.id = "registry-id"
            mock_registry.async_get_device.return_value = mock_device

            select_result = await flow.async_step_select_device({CONF_DEVICE_ID: "dev-2"})
            assert select_result["type"] == "menu"

            flow._pending_action = "edit_device"
            flow._selected_device_id = "dev-2"

            result = await flow.async_step_edit_device(
                {
                    CONF_NAME: "Updated Device",
                    CONF_MANUFACTURER: "New Maker",
                    CONF_MODEL: "New Model",
                    CONF_SW_VERSION: "3.0",
                    CONF_HW_VERSION: "3.0",
                }
            )

        assert result["type"] == "create_entry"
        call_kwargs = flow.hass.config_entries.async_update_entry.call_args.kwargs
        devices = call_kwargs["data"]["devices"]
        assert devices[1][CONF_NAME] == "Updated Device"
        assert devices[0][CONF_NAME] == "Device 1"
        mock_registry.async_update_device.assert_called_once_with("registry-id", name_by_user=None)
        assert config_entry.data["devices"][1][CONF_NAME] == "Device 2"

    @pytest.mark.asyncio
    async def test_delete_device_removes_selected_device(self):
        """Test deleting a selected device removes only that device."""
        flow, _config_entry = self._build_flow(
            devices=[
                {"id": "dev-1", CONF_NAME: "Device 1"},
                {"id": "dev-2", CONF_NAME: "Device 2"},
            ]
        )
        flow._selected_device_id = "dev-2"
        flow._pending_action = "delete_device"

        result = await flow.async_step_delete_device({CONF_CONFIRM_DELETE: True})

        assert result["type"] == "create_entry"
        call_kwargs = flow.hass.config_entries.async_update_entry.call_args.kwargs
        assert len(call_kwargs["data"]["devices"]) == 1
        assert call_kwargs["data"]["devices"][0]["id"] == "dev-1"

    @pytest.mark.asyncio
    async def test_delete_last_device_removes_it(self):
        """Test deleting the last device leaves an empty group."""
        flow, _config_entry = self._build_flow(devices=[{"id": "dev-1", CONF_NAME: "Only Device"}])
        flow._selected_device_id = "dev-1"
        flow._pending_action = "delete_device"

        result = await flow.async_step_delete_device({CONF_CONFIRM_DELETE: True})

        assert result["type"] == "create_entry"
        call_kwargs = flow.hass.config_entries.async_update_entry.call_args.kwargs
        assert call_kwargs["data"]["devices"] == []

    @pytest.mark.asyncio
    async def test_move_device_aborts_without_other_hubs(self):
        """Test moving a device aborts when there is no destination hub."""
        flow, _config_entry = self._build_flow(devices=[{"id": "dev-1", CONF_NAME: "Only Device"}])
        flow._selected_device_id = "dev-1"

        result = await flow.async_step_move_device()

        assert result["type"] == "abort"
        assert result["reason"] == "no_target_entries"

    @pytest.mark.asyncio
    async def test_move_device_shows_target_selector(self):
        """Test moving a device shows the destination hub selector."""
        flow, config_entry = self._build_flow(devices=[{"id": "dev-1", CONF_NAME: "Only Device"}])
        other_entry = MagicMock()
        other_entry.entry_id = "entry-other"
        other_entry.title = "Other"
        other_entry.data = {"devices": []}
        flow.hass.config_entries.async_entries.return_value = [config_entry, other_entry]
        flow._selected_device_id = "dev-1"

        result = await flow.async_step_move_device()

        assert result["type"] == "form"
        assert result["step_id"] == "select_target_entry"

    @pytest.mark.asyncio
    async def test_move_device_rejects_duplicate_name_in_target(self):
        """Test moving a device rejects duplicate names in the destination hub."""
        flow, config_entry = self._build_flow(devices=[{"id": "dev-1", CONF_NAME: "Sensor"}])
        other_entry = MagicMock()
        other_entry.entry_id = "entry-other"
        other_entry.title = "Other"
        other_entry.data = {"devices": [{"id": "dev-2", CONF_NAME: "Sensor"}]}
        flow.hass.config_entries.async_entries.return_value = [config_entry, other_entry]
        flow._selected_device_id = "dev-1"

        result = await flow.async_step_select_target_entry({CONF_TARGET_ENTRY_ID: "entry-other"})

        assert result["type"] == "form"
        assert result["errors"]["base"] == "name_already_exists"

    @pytest.mark.asyncio
    async def test_move_device_moves_selected_device_to_other_hub(self):
        """Test moving a device updates both hubs and reassigns the registry link."""
        flow, config_entry = self._build_flow(
            devices=[
                {"id": "dev-1", CONF_NAME: "Device 1"},
                {"id": "dev-2", CONF_NAME: "Device 2"},
            ],
            title="Source",
        )
        other_entry = MagicMock()
        other_entry.entry_id = "entry-target"
        other_entry.title = "Target"
        other_entry.data = {"devices": [{"id": "dev-3", CONF_NAME: "Existing"}]}
        flow.hass.config_entries.async_entries.return_value = [config_entry, other_entry]
        registry = MagicMock()
        registry_device = MagicMock()
        registry_device.id = "registry-id"
        registry.async_get_device.return_value = registry_device

        with patch("custom_components.simple_device_creator.config_flow.dr.async_get", return_value=registry):
            flow._selected_device_id = "dev-2"
            result = await flow.async_step_select_target_entry({CONF_TARGET_ENTRY_ID: "entry-target"})

        assert result["type"] == "create_entry"
        update_calls = flow.hass.config_entries.async_update_entry.call_args_list
        assert len(update_calls) == 2
        target_call = update_calls[0].kwargs
        source_call = update_calls[1].kwargs
        assert target_call["data"]["devices"][1]["id"] == "dev-2"
        assert [device["id"] for device in source_call["data"]["devices"]] == ["dev-1"]
        registry.async_get_or_create.assert_called_once()
        registry.async_update_device.assert_called_once_with(
            "registry-id", remove_config_entry_id=config_entry.entry_id
        )