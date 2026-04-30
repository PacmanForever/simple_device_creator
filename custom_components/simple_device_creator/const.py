"""Constants for Simple Device Creator integration."""
DOMAIN = "simple_device_creator"
PLATFORMS = []  # No platforms, only devices

# Device configuration keys
CONF_ENTRY_TITLE = "entry_title"
CONF_NAME = "name"
CONF_MANUFACTURER = "manufacturer"
CONF_MODEL = "model"
CONF_SW_VERSION = "sw_version"
CONF_HW_VERSION = "hw_version"

# Menu options for config flow
MENU_ADD_DEVICE = "add_device"
MENU_EDIT_DEVICE = "edit_device"
MENU_DELETE_DEVICE = "delete_device"
MENU_MOVE_DEVICE = "move_device"
MENU_RENAME_ENTRY = "rename_entry"
MENU_FINISH = "finish"

# Menu options list
MENU_OPTIONS = [
    MENU_ADD_DEVICE,
    MENU_EDIT_DEVICE,
    MENU_DELETE_DEVICE,
    MENU_MOVE_DEVICE,
    MENU_RENAME_ENTRY,
    MENU_FINISH,
]

# Default device values
DEFAULT_ENTRY_TITLE = "General"
DEFAULT_DEVICE_NAME = "New Device"
DEFAULT_MANUFACTURER = ""
DEFAULT_MODEL = ""
DEFAULT_SW_VERSION = ""
DEFAULT_HW_VERSION = ""
