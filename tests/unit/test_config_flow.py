"""Test config flow."""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.simple_device_creator.config_flow import (
    SimpleDeviceCreatorConfigFlow,
    SimpleDeviceCreatorOptionsFlow,
)
from custom_components.simple_device_creator.const import (
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
    MENU_CREATE_DEVICE,
    MENU_EDIT_DEVICE,
    MENU_DELETE_DEVICE,
    MENU_FINISH,
)


class TestSimpleDeviceCreatorConfigFlow:
    """Test the config flow."""

    def test_init(self):
        """Test initialization."""
        flow = SimpleDeviceCreatorConfigFlow()
        assert flow.devices == []

    @pytest.mark.asyncio
    async def test_step_user_menu_finish(self):
        """Test menu finish."""
        flow = SimpleDeviceCreatorConfigFlow()
        flow.devices = [{"id": "test", "name": "Test"}]

        result = await flow.async_step_user({"menu_option": MENU_FINISH})

        assert result["type"] == "create_entry"
        assert result["data"]["devices"] == flow.devices

    @pytest.mark.asyncio
    async def test_step_user_menu_create(self):
        """Test menu create device."""
        flow = SimpleDeviceCreatorConfigFlow()

        result = await flow.async_step_user({"menu_option": MENU_CREATE_DEVICE})

        assert result["type"] == "form"
        assert result["step_id"] == "create_device"

    @pytest.mark.asyncio
    async def test_step_user_menu_edit(self):
        """Test menu edit device."""
        flow = SimpleDeviceCreatorConfigFlow()
        flow.devices = [{"id": "test", "name": "Test"}]

        result = await flow.async_step_user({"menu_option": MENU_EDIT_DEVICE})

        assert result["type"] == "form"
        assert result["step_id"] == "select_device"

    @pytest.mark.asyncio
    async def test_step_user_menu_delete(self):
        """Test menu delete device."""
        flow = SimpleDeviceCreatorConfigFlow()
        flow.devices = [{"id": "test", "name": "Test"}]

        result = await flow.async_step_user({"menu_option": MENU_DELETE_DEVICE})

        assert result["type"] == "form"
        assert result["step_id"] == "select_device"

    @pytest.mark.asyncio
    async def test_step_user_show_form(self):
        """Test user step shows form."""
        flow = SimpleDeviceCreatorConfigFlow()

        result = await flow.async_step_user()

        assert result["type"] == "form"
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_step_user_invalid_option(self):
        """Test user step with invalid menu option."""
        flow = SimpleDeviceCreatorConfigFlow()

        result = await flow.async_step_user({"menu_option": "invalid"})

        assert result["type"] == "form"
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_step_create_device_success(self):
        """Test creating a device successfully."""
        flow = SimpleDeviceCreatorConfigFlow()

        user_input = {
            CONF_NAME: "Test Device",
            CONF_MANUFACTURER: "Test Manufacturer",
            CONF_MODEL: "Test Model",
            CONF_SW_VERSION: "1.0.0",
            CONF_HW_VERSION: "1.0",
            CONF_CONFIGURATION_URL: "http://example.com",
            CONF_CONNECTIONS: "mac:AA:BB:CC:DD:EE:FF",
        }

        result = await flow.async_step_create_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "user"
        assert len(flow.devices) == 1
        device = flow.devices[0]
        assert device[CONF_NAME] == "Test Device"
        assert device[CONF_MANUFACTURER] == "Test Manufacturer"
        assert device[CONF_CONNECTIONS] == [("mac", "AA:BB:CC:DD:EE:FF")]

    @pytest.mark.asyncio
    async def test_step_create_device_invalid_connections(self):
        """Test creating a device with invalid connections."""
        flow = SimpleDeviceCreatorConfigFlow()

        user_input = {
            CONF_NAME: "Test Device",
            CONF_MANUFACTURER: "",
            CONF_MODEL: "",
            CONF_SW_VERSION: "",
            CONF_HW_VERSION: "",
            CONF_CONFIGURATION_URL: "",
            CONF_CONNECTIONS: "invalid",
        }

        result = await flow.async_step_create_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "create_device"
        assert result["errors"]["connections"] == "invalid_format"
        assert len(flow.devices) == 0

    @pytest.mark.asyncio
    async def test_step_create_device_duplicate_name(self):
        """Test creating a device with duplicate name."""
        flow = SimpleDeviceCreatorConfigFlow()
        flow.devices = [{"id": "1", "name": "Existing Device"}]

        user_input = {
            CONF_NAME: "Existing Device",
            CONF_MANUFACTURER: "",
            CONF_MODEL: "",
            CONF_SW_VERSION: "",
            CONF_HW_VERSION: "",
            CONF_CONFIGURATION_URL: "",
            CONF_CONNECTIONS: "",
        }

        result = await flow.async_step_create_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "create_device"
        assert result["errors"]["name"] == "name_already_exists"
        assert len(flow.devices) == 1

    @pytest.mark.asyncio
    async def test_step_select_device_no_devices(self):
        """Test selecting device when none exist."""
        flow = SimpleDeviceCreatorConfigFlow()

        result = await flow.async_step_select_device()

        assert result["type"] == "form"
        assert result["step_id"] == "user"
    @pytest.mark.asyncio
    async def test_step_select_device_show_form(self):
        """Test select device shows form."""
        flow = SimpleDeviceCreatorConfigFlow()
        flow.devices = [{"id": "test", "name": "Test"}]

        result = await flow.async_step_select_device()

        assert result["type"] == "form"
        assert result["step_id"] == "select_device"
    @pytest.mark.asyncio
    async def test_step_select_device_delete(self):
        """Test deleting a device."""
        flow = SimpleDeviceCreatorConfigFlow()
        device_id = str(uuid.uuid4())
        flow.devices = [{"id": device_id, "name": "Test"}]

        result = await flow.async_step_select_device({"device_id": device_id}, delete=True)

        assert result["type"] == "form"
        assert result["step_id"] == "user"
        assert len(flow.devices) == 0

    @pytest.mark.asyncio
    async def test_step_select_device_edit(self):
        """Test selecting device for edit."""
        flow = SimpleDeviceCreatorConfigFlow()
        device_id = str(uuid.uuid4())
        flow.devices = [{"id": device_id, "name": "Test"}]

        result = await flow.async_step_select_device({"device_id": device_id}, delete=False)

        assert result["type"] == "form"
        assert result["step_id"] == "edit_device"
        assert flow.selected_device_id == device_id

    @pytest.mark.asyncio
    async def test_step_edit_device_success(self):
        """Test editing a device successfully."""
        flow = SimpleDeviceCreatorConfigFlow()
        device_id = str(uuid.uuid4())
        flow.devices = [{"id": device_id, "name": "Old Name"}]
        flow.selected_device_id = device_id

        user_input = {
            CONF_NAME: "New Name",
            CONF_MANUFACTURER: "",
            CONF_MODEL: "",
            CONF_SW_VERSION: "",
            CONF_HW_VERSION: "",
            CONF_CONFIGURATION_URL: "",
            CONF_CONNECTIONS: "",
        }

        result = await flow.async_step_edit_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "user"
        assert flow.devices[0][CONF_NAME] == "New Name"

    @pytest.mark.asyncio
    async def test_step_edit_device_duplicate_name(self):
        """Test editing a device with duplicate name."""
        flow = SimpleDeviceCreatorConfigFlow()
        device_id = str(uuid.uuid4())
        flow.devices = [
            {"id": device_id, "name": "Device 1", "connections": []},
            {"id": str(uuid.uuid4()), "name": "Device 2", "connections": []}
        ]
        flow.selected_device_id = device_id

        user_input = {
            CONF_NAME: "Device 2",
            CONF_MANUFACTURER: "",
            CONF_MODEL: "",
            CONF_SW_VERSION: "",
            CONF_HW_VERSION: "",
            CONF_CONFIGURATION_URL: "",
            CONF_CONNECTIONS: "",
        }

        result = await flow.async_step_edit_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "edit_device"
        assert result["errors"]["name"] == "name_already_exists"
        assert flow.devices[0][CONF_NAME] == "Device 1"  # unchanged

    @pytest.mark.asyncio
    async def test_step_edit_device_invalid_connections(self):
        """Test editing a device with invalid connections."""
        flow = SimpleDeviceCreatorConfigFlow()
        device_id = str(uuid.uuid4())
        flow.devices = [{"id": device_id, "name": "Test", "connections": []}]
        flow.selected_device_id = device_id

        user_input = {
            CONF_NAME: "Test",
            CONF_MANUFACTURER: "",
            CONF_MODEL: "",
            CONF_SW_VERSION: "",
            CONF_HW_VERSION: "",
            CONF_CONFIGURATION_URL: "",
            CONF_CONNECTIONS: "invalid",
        }

        result = await flow.async_step_edit_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "edit_device"
        assert result["errors"]["connections"] == "invalid_format"
        assert flow.devices[0][CONF_CONNECTIONS] == []  # unchanged


class TestSimpleDeviceCreatorOptionsFlow:
    """Test the options flow."""

    def test_init(self):
        """Test initialization."""
        config_entry = MagicMock()
        config_entry.data = {"devices": []}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        assert flow.devices == []

    @pytest.mark.asyncio
    async def test_step_init(self):
        """Test init step."""
        config_entry = MagicMock()
        config_entry.data = {"devices": []}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        result = await flow.async_step_init()

        assert result["type"] == "form"
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_step_user_menu_finish(self):
        """Test options menu finish."""
        config_entry = MagicMock()
        config_entry.data = {"devices": []}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        flow.devices = [{"id": "test", "name": "Test"}]

        result = await flow.async_step_user({"menu_option": MENU_FINISH})

        assert result["type"] == "create_entry"
        assert result["data"]["devices"] == flow.devices

    @pytest.mark.asyncio
    async def test_step_user_menu_create(self):
        """Test options menu create device."""
        config_entry = MagicMock()
        config_entry.data = {"devices": []}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        result = await flow.async_step_user({"menu_option": MENU_CREATE_DEVICE})

        assert result["type"] == "form"
        assert result["step_id"] == "create_device"

    @pytest.mark.asyncio
    async def test_step_create_device_options_success(self):
        """Test creating a device in options successfully."""
        config_entry = MagicMock()
        config_entry.data = {"devices": []}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        user_input = {
            CONF_NAME: "Test Device",
            CONF_MANUFACTURER: "Test Manufacturer",
            CONF_MODEL: "Test Model",
            CONF_SW_VERSION: "1.0.0",
            CONF_HW_VERSION: "1.0",
            CONF_CONFIGURATION_URL: "http://example.com",
            CONF_CONNECTIONS: "mac:AA:BB:CC:DD:EE:FF",
        }

        result = await flow.async_step_create_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "user"
        assert len(flow.devices) == 1
        device = flow.devices[0]
        assert device[CONF_NAME] == "Test Device"
        assert device[CONF_MANUFACTURER] == "Test Manufacturer"
        assert device[CONF_CONNECTIONS] == [("mac", "AA:BB:CC:DD:EE:FF")]

    @pytest.mark.asyncio
    async def test_step_create_device_duplicate_name_options(self):
        """Test creating a device with duplicate name in options."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [{"id": "existing", "name": "Existing Device"}]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        user_input = {
            CONF_NAME: "Existing Device",
            CONF_MANUFACTURER: "",
            CONF_MODEL: "",
            CONF_SW_VERSION: "",
            CONF_HW_VERSION: "",
            CONF_CONFIGURATION_URL: "",
            CONF_CONNECTIONS: "",
        }

        result = await flow.async_step_create_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "create_device"
        assert result["errors"]["name"] == "name_already_exists"
        assert len(flow.devices) == 1

    @pytest.mark.asyncio
    async def test_step_user_menu_edit(self):
        """Test options menu edit device."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [{"id": "test", "name": "Test"}]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        result = await flow.async_step_user({"menu_option": MENU_EDIT_DEVICE})

        assert result["type"] == "form"
        assert result["step_id"] == "select_device"

    @pytest.mark.asyncio
    async def test_step_user_menu_delete(self):
        """Test options menu delete device."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [{"id": "test", "name": "Test"}]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        result = await flow.async_step_user({"menu_option": MENU_DELETE_DEVICE})

        assert result["type"] == "form"
        assert result["step_id"] == "select_device"

    @pytest.mark.asyncio
    async def test_step_user_invalid_option(self):
        """Test options user step with invalid menu option."""
        config_entry = MagicMock()
        config_entry.data = {"devices": []}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        result = await flow.async_step_user({"menu_option": "invalid"})

        assert result["type"] == "form"
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_step_select_device_edit(self):
        """Test selecting device for edit."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [{"id": "test", "name": "Test"}]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        result = await flow.async_step_select_device({"device_id": "test"})

        assert result["type"] == "form"
        assert result["step_id"] == "edit_device"
        assert flow.selected_device_id == "test"

    @pytest.mark.asyncio
    async def test_step_select_device_delete(self):
        """Test selecting device for delete."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [{"id": "test", "name": "Test"}]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        result = await flow.async_step_select_device({"device_id": "test"}, delete=True)

        assert result["type"] == "form"
        assert result["step_id"] == "user"
        assert len(flow.devices) == 0

    @pytest.mark.asyncio
    async def test_step_select_device_no_devices(self):
        """Test select device when no devices."""
        config_entry = MagicMock()
        config_entry.data = {"devices": []}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        result = await flow.async_step_select_device()

        assert result["type"] == "form"
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_step_select_device_show_form(self):
        """Test select device shows form."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [{"id": "test", "name": "Test"}]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        result = await flow.async_step_select_device()

        assert result["type"] == "form"
        assert result["step_id"] == "select_device"

    @pytest.mark.asyncio
    async def test_step_select_device_show_form_delete(self):
        """Test select device shows form for delete."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [{"id": "test", "name": "Test"}]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)

        result = await flow.async_step_select_device(delete=True)

        assert result["type"] == "form"
        assert result["step_id"] == "select_device"

    @pytest.mark.asyncio
    async def test_step_edit_device_success(self):
        """Test editing device successfully."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [{"id": "test", "name": "Test", "manufacturer": "Old"}]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        flow.selected_device_id = "test"

        user_input = {
            CONF_NAME: "Updated Test",
            CONF_MANUFACTURER: "New Manufacturer",
            CONF_MODEL: "Test Model",
            CONF_SW_VERSION: "1.0.0",
            CONF_HW_VERSION: "1.0",
            CONF_CONFIGURATION_URL: "http://example.com",
            CONF_CONNECTIONS: "mac:AA:BB:CC:DD:EE:FF",
        }

        result = await flow.async_step_edit_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "user"
        assert flow.devices[0][CONF_NAME] == "Updated Test"
        assert flow.devices[0][CONF_MANUFACTURER] == "New Manufacturer"

    @pytest.mark.asyncio
    async def test_step_edit_device_duplicate_name_options(self):
        """Test editing a device with duplicate name in options."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [
            {"id": "test1", "name": "Device 1", "connections": []},
            {"id": "test2", "name": "Device 2", "connections": []}
        ]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        flow.selected_device_id = "test1"

        user_input = {
            CONF_NAME: "Device 2",
            CONF_MANUFACTURER: "",
            CONF_MODEL: "",
            CONF_SW_VERSION: "",
            CONF_HW_VERSION: "",
            CONF_CONFIGURATION_URL: "",
            CONF_CONNECTIONS: "",
        }

        result = await flow.async_step_edit_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "edit_device"
        assert result["errors"]["name"] == "name_already_exists"
        assert flow.devices[0][CONF_NAME] == "Device 1"  # unchanged

    @pytest.mark.asyncio
    async def test_step_edit_device_invalid_connections_options(self):
        """Test editing a device with invalid connections in options."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [{"id": "test", "name": "Test", "connections": []}]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        flow.selected_device_id = "test"

        user_input = {
            CONF_NAME: "Test",
            CONF_MANUFACTURER: "",
            CONF_MODEL: "",
            CONF_SW_VERSION: "",
            CONF_HW_VERSION: "",
            CONF_CONFIGURATION_URL: "",
            CONF_CONNECTIONS: "invalid",
        }

        result = await flow.async_step_edit_device(user_input)

        assert result["type"] == "form"
        assert result["step_id"] == "edit_device"
        assert result["errors"]["connections"] == "invalid_format"
        assert flow.devices[0][CONF_CONNECTIONS] == []  # unchanged

    @pytest.mark.asyncio
    async def test_step_edit_device_show_form(self):
        """Test edit device shows form."""
        config_entry = MagicMock()
        config_entry.data = {"devices": [{"id": "test", "name": "Test", "connections": [("mac", "AA:BB")]}]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        flow.selected_device_id = "test"

        result = await flow.async_step_edit_device()

        assert result["type"] == "form"
        assert result["step_id"] == "edit_device"