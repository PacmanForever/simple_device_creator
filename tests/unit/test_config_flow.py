"""Test config flow."""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.simple_device_creator.config_flow import (
    SimpleDeviceCreatorConfigFlow,
    SimpleDeviceCreatorOptionsFlow,
)
from custom_components.simple_device_creator.const import (
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


class TestSimpleDeviceCreatorConfigFlow:
    """Test the config flow."""

    def test_init(self):
        """Test initialization."""
        flow = SimpleDeviceCreatorConfigFlow()
        assert flow.devices == []

    @pytest.mark.asyncio
    async def test_step_user_show_form(self):
        """Test user step shows form."""
        flow = SimpleDeviceCreatorConfigFlow()

        result = await flow.async_step_user()

        assert result["type"] == "form"
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_step_user_create_entry(self):
        """Test creating entry from user step."""
        flow = SimpleDeviceCreatorConfigFlow()

        user_input = {
            CONF_NAME: "Test Device",
            CONF_MANUFACTURER: "Test Manufacturer",
            CONF_MODEL: "Test Model",
            CONF_SW_VERSION: "1.0.0",
            CONF_HW_VERSION: "1.0",
        }

        result = await flow.async_step_user(user_input)

        assert result["type"] == "create_entry"
        assert result["title"] == "Test Device"
        assert len(result["data"]["devices"]) == 1
        device = result["data"]["devices"][0]
        assert device[CONF_NAME] == "Test Device"

    def test_async_get_options_flow(self):
        """Test get options flow."""
        config_entry = MagicMock()
        flow = SimpleDeviceCreatorConfigFlow.async_get_options_flow(config_entry)
        assert isinstance(flow, SimpleDeviceCreatorOptionsFlow)


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
        """Test init step calling user step."""
        config_entry = MagicMock()
        config_entry.data = {"devices": []}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        
        # Mock step user to return something
        flow.async_step_user = AsyncMock(return_value="mock_result")
        
        result = await flow.async_step_init()
        assert result == "mock_result"
        flow.async_step_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_step_user_no_devices(self):
        """Test user step when no devices exist."""
        config_entry = MagicMock()
        config_entry.data = {"devices": []}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        
        result = await flow.async_step_user()
        
        assert result["type"] == "create_entry"
        assert result["data"]["devices"] == []

    @pytest.mark.asyncio
    async def test_step_user_show_form(self):
        """Test user step shows form with device data."""
        config_entry = MagicMock()
        device_data = {
            "id": "test",
            CONF_NAME: "Test Device",
            CONF_MANUFACTURER: "Old Man",
            CONF_MODEL: "Old Mod",
            CONF_SW_VERSION: "1.0",
            CONF_HW_VERSION: "1.0"
        }
        config_entry.data = {"devices": [device_data]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        flow.hass = MagicMock()

        # Mock Registry
        with patch("custom_components.simple_device_creator.config_flow.dr.async_get") as mock_dr_get:
            mock_registry = MagicMock()
            mock_dr_get.return_value = mock_registry
            mock_registry.async_get_device.return_value = None # No existing device in registry

            result = await flow.async_step_user()
            
            assert result["type"] == "form"
            assert result["step_id"] == "user"
            # Check defaults are populated
            schema = result["data_schema"].schema
            # Find key for CONF_NAME
            name_key = next(k for k in schema if str(k) == CONF_NAME)
            val = name_key.default
            if callable(val):
                val = val()
            assert val == "Test Device"

    @pytest.mark.asyncio
    async def test_step_user_show_form_sync_registry(self):
        """Test user step shows form with device data synced from registry."""
        config_entry = MagicMock()
        device_data = {
            "id": "test",
            CONF_NAME: "Old Config Name",
            CONF_MANUFACTURER: "Old config Man",
        }
        config_entry.data = {"devices": [device_data]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        flow.hass = MagicMock()

        # Mock Registry
        with patch("custom_components.simple_device_creator.config_flow.dr.async_get") as mock_dr_get:
            mock_registry = MagicMock()
            mock_dr_get.return_value = mock_registry
            
            mock_device = MagicMock()
            mock_device.name_by_user = "Renamed by User"
            mock_device.name = "Registry Name"
            # Simulate matching device found
            mock_registry.async_get_device.return_value = mock_device

            result = await flow.async_step_user()
            
            assert result["type"] == "form"
            schema = result["data_schema"].schema
            name_key = next(k for k in schema if str(k) == CONF_NAME)
            val = name_key.default
            if callable(val):
                val = val()
            
            # Should prefer name_by_user
            assert val == "Renamed by User"
            mock_registry.async_get_device.assert_called_with(identifiers={(DOMAIN, "test")})


    @pytest.mark.asyncio
    async def test_step_user_edit_success(self):
        """Test editing device successfully."""
        config_entry = MagicMock()
        device_data = {
            "id": "test",
            CONF_NAME: "Test Device",
            CONF_MANUFACTURER: "Old Man",
            CONF_MODEL: "Old Mod",
            CONF_SW_VERSION: "1.0",
            CONF_HW_VERSION: "1.0"
        }
        config_entry.data = {"devices": [device_data]}
        flow = SimpleDeviceCreatorOptionsFlow(config_entry)
        flow.hass = MagicMock()
        
        user_input = {
            CONF_NAME: "New Name",
            CONF_MANUFACTURER: "New Man",
            CONF_MODEL: "New Mod",
            CONF_SW_VERSION: "2.0",
            CONF_HW_VERSION: "2.0",
        }
        
        with patch("custom_components.simple_device_creator.config_flow.dr.async_get") as mock_dr_get:
            mock_registry = MagicMock()
            mock_dr_get.return_value = mock_registry
            mock_device = MagicMock()
            mock_device.id = "device_reg_id"
            mock_registry.async_get_device.return_value = mock_device

            result = await flow.async_step_user(user_input)
            
            assert result["type"] == "create_entry"
            assert len(result["data"]["devices"]) == 1
            device = result["data"]["devices"][0]
            assert device[CONF_NAME] == "New Name"
            assert device[CONF_MANUFACTURER] == "New Man"
            assert device["id"] == "test"
            
            # Verify registry update was called to clear name_by_user
            mock_registry.async_update_device.assert_called_with("device_reg_id", name_by_user=None)
