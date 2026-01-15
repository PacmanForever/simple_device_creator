"""Constants for Simple Device Creator integration."""
DOMAIN = "simple_device_creator"
PLATFORMS = []  # No platforms, only devices

# Device configuration keys
CONF_NAME = "name"
CONF_MANUFACTURER = "manufacturer"
CONF_MODEL = "model"
CONF_SW_VERSION = "sw_version"
CONF_HW_VERSION = "hw_version"

# Menu options for config flow
MENU_CREATE_DEVICE = "create_device"
MENU_EDIT_DEVICE = "edit_device"
MENU_FINISH = "finish"

# Menu options list
MENU_OPTIONS = [
    MENU_CREATE_DEVICE,
    MENU_EDIT_DEVICE,
    MENU_FINISH,
]

# Default device values
DEFAULT_DEVICE_NAME = "New Device"
DEFAULT_MANUFACTURER = ""
DEFAULT_MODEL = ""
DEFAULT_SW_VERSION = ""
DEFAULT_HW_VERSION = ""
