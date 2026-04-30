# AI Development Guidelines & Critical Implementation Details

This document serves as a reference for AI agents and developers working on the `simple_device_creator` integration to prevent regression of known issues and ensure architectural consistency.

## 1. Device Registry Management

### Synchronization Strategy
The integration manages devices solely based on the configuration entry data. The `async_setup_entry` function must act as a source of truth synchronizer.

- **Creation/Update**: Iterate through configured devices and call `device_reg.async_get_or_create`.
- **Pruning (CRITICAL)**: You must explicitly check for and remove orphan devices that exist in the Home Assistant device registry but are no longer present in the config entry.
    - *Mechanism*: Collect all valid device IDs during creation. Then iterate through `dr.async_entries_for_config_entry` and remove any device whose identifier is not in the valid set.

### API Behavior
- **`device_reg.async_get_or_create`**:
    - **Type**: Synchronous method (despite the `async_` prefix naming convention in older HA versions or specific helpers).
    - **Return**: Returns the `DeviceEntry` object immediately, not a coroutine.
    - **Testing**: When mocking this method in tests, use `MagicMock`, NOT `AsyncMock`. Using `AsyncMock` will cause `RuntimeWarning: coroutine ... was never awaited` because the code will treat the mock as a value, not an awaitable.

## 2. Config Flow & Options Flow

### Current Scope
- The current UI flow creates one config entry that can collect zero or more virtual devices during setup.
- The options flow supports adding, editing, moving, and deleting devices, and renaming the entry/group title, including deleting the last remaining device in a group.
- Supported fields are limited to `name`, `manufacturer`, `model`, `sw_version`, and `hw_version`.
- There is currently no `connections` or `configuration_url` handling in the live code.
- Legacy single-device entries are migrated into one entry initially titled `General`.

### Update Listeners
- The integration supports dynamic reconfiguration via Options Flow.
- Ensure `entry.add_update_listener(async_reload_entry)` is registered in `async_setup_entry`.
- This ensures that when a user adds, edits, or deletes devices in the Options menu, the integration reloads and the `async_setup_entry` logic (including pruning) is re-executed immediately.

### Rename Synchronization
- Renaming the device from the Home Assistant device registry sets `name_by_user` on the registry entry.
- `async_setup_entry` and the device registry update listener must sync that name back into the matching stored device name.
- The config entry title is an independent group name and must not be changed by device renames.
- After syncing, clear `name_by_user` so the integration-owned name becomes authoritative again.

### Cross-Entry Device Moves
- Moving a device between hub entries must preserve the same device-registry device identity.
- Do not implement hub moves as delete-and-recreate if registry identity can be preserved.
- When moving a device, add the destination config entry to the registry device, then remove the source config entry association, and finally update both entries' stored `devices` lists.

## 3. Testing

### Mocking Registry
- When testing `async_setup_entry`, mock both `dr.async_get` and `dr.async_entries_for_config_entry`.
- Ensure tests cover the scenario of "removing a device" to verify the pruning logic works.
