# Copilot Instructions — Simple Device Creator

## Project

Custom Home Assistant integration for creating virtual device groups without associated entities.

- **Repo**: `PacmanForever/simple_device_creator`
- **Domain**: `simple_device_creator`
- **Code language**: English (comments, docstrings, variable names)
- **User-facing communication language**: Catalan when speaking with the user

## Development Environment

- **OS**: Linux (Debian/Ubuntu)
- **Python**: 3.13 in the root `venv/`
- **Tests**: pytest, pytest-cov, pytest-asyncio, pytest-homeassistant-custom-component
- **Coverage target**: Silver level or better, minimum >=95% across the full package
- **Current verified state**: 98% coverage for the `custom_components.simple_device_creator` package

## Code Architecture

- `custom_components/simple_device_creator/__init__.py`: main synchronization with the device registry, orphan pruning, legacy entry migration, rename listener, and setup/unload
- `custom_components/simple_device_creator/config_flow.py`: initial config flow and options flow for managing device groups and devices
- `custom_components/simple_device_creator/const.py`: domain constants and default values
- `custom_components/simple_device_creator/strings.json`: config flow and options flow text
- `tests/unit/`: coverage for config flow, init, rename sync, and constants
- `tests/component/`: integration tests with Home Assistant

## Conventions

- Use English for commits if commits are made outside chat
- Keep code and comments in English
- Keep responses and explanations in Catalan when speaking with the user
- Prioritize correctness, simplicity, and consistency with Home Assistant patterns
- Run tests before considering a task complete if code or tests were changed
- Do not create summary `.md` files unless explicitly requested

## Current Functional Behavior

- The integration creates one config entry that can own zero or more virtual devices
- The currently supported fields are `name`, `manufacturer`, `model`, `sw_version`, and `hw_version`
- The options flow supports adding, editing, moving, deleting devices, and renaming the group entry title
- There is currently no implemented support for `connections` or `configuration_url`
- Device renames from the Home Assistant device registry must synchronize back to the matching stored device only
- The config entry title is an independent group name
- A group entry may remain empty, including after deleting its last device
- Legacy single-device entries are consolidated into one migrated entry initially named `General`

## Critical Implementation Rules

- `async_setup_entry` is the source of truth for synchronizing the device registry
- Always prune registry devices that no longer exist in `entry.data`
- `device_reg.async_get_or_create` is synchronous in this context and must be mocked with `MagicMock`, not `AsyncMock`
- If a device has `name_by_user`, synchronize it back into the matching stored device record
- After synchronizing a rename, clear `name_by_user` so the integration-owned name becomes authoritative again
- Moving a device between entries should preserve the same device-registry device identity instead of recreating it
- Preserve backward compatibility by supporting legacy entry migration into a `General` group without forcing users to recreate devices

## Recommended HA Patterns

- Keep `integration_type` in `manifest.json` aligned with the current UI model and Home Assistant config-flow support; `hub` is the chosen compromise because `helper` and `virtual` produced worse tradeoffs in practice
- Evaluate migrating from `hass.data[DOMAIN][entry_id]` to `entry.runtime_data`
- Keep listeners and setup aligned with Home Assistant config entry reload patterns

## Practical Environment Notes

- If `venv/bin/python` loses its execute bit, run `chmod +x venv/bin/python` before executing local tests
