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

### Connection Parsing
- Device connections (MAC, IP, etc.) are entered as comma-separated strings (e.g., `mac:xx:xx, ip:1.2.3.4`).
- **DRY Principle**: Validation and parsing logic for these strings is centralized in the `parse_connections` helper function within `config_flow.py`. Do not duplicate this logic in `async_step_create_device` or `async_step_edit_device`.

### Update Listeners
- The integration supports dynamic reconfiguration via Options Flow.
- Ensure `entry.add_update_listener(async_reload_entry)` is registered in `async_setup_entry`.
- This ensures that when a user adds/edits/deletes a device in the Options menu, the integration reloads and the `async_setup_entry` logic (including pruning) is re-executed immediately.

## 3. Testing

### Mocking Registry
- When testing `async_setup_entry`, mock both `dr.async_get` and `dr.async_entries_for_config_entry`.
- Ensure tests cover the scenario of "removing a device" to verify the pruning logic works.
