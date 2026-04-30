# Simple Device Creator

[![hacs](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Version](https://img.shields.io/github/v/release/PacmanForever/simple_device_creator?label=version)](https://github.com/PacmanForever/simple_device_creator/releases)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
[![Unit Tests](https://github.com/PacmanForever/simple_device_creator/actions/workflows/tests_unit.yml/badge.svg)](https://github.com/PacmanForever/simple_device_creator/actions/workflows/tests_unit.yml)
[![Component Tests](https://github.com/PacmanForever/simple_device_creator/actions/workflows/tests_component.yml/badge.svg)](https://github.com/PacmanForever/simple_device_creator/actions/workflows/tests_component.yml)
[![Validate HACS](https://github.com/PacmanForever/simple_device_creator/actions/workflows/validate_hacs.yml/badge.svg)](https://github.com/PacmanForever/simple_device_creator/actions/workflows/validate_hacs.yml)
[![Validate Hassfest](https://github.com/PacmanForever/simple_device_creator/actions/workflows/validate_hassfest.yml/badge.svg)](https://github.com/PacmanForever/simple_device_creator/actions/workflows/validate_hassfest.yml)

![Home Assistant](https://img.shields.io/badge/home%20assistant-2024.1.0%2B-blue)

> [!IMPORTANT]
> **Beta:** This integration is in *beta* phase. Correct functioning is not guaranteed and may contain errors; use it at your own risk.

A Home Assistant integration that allows users to create virtual device groups without entities.

## What This Integration Does

Simple Device Creator lets you create entries in Home Assistant that manage virtual devices in the device registry.

Each integration entry acts as a group:

- The entry title is the group name
- Each group can contain zero, one, or many virtual devices
- Each virtual device can store basic metadata such as name, manufacturer, model, software version, and hardware version

This is useful when you want a device to exist in Home Assistant before you have entities attached to it, or when you want to organize devices manually around your own structure.

## How It Works

The integration does not create entities. It only creates and maintains device registry entries.

In practice, that means:

- A created device appears in Home Assistant as a device
- That device has no sensors, switches, or other entities by default
- You can later associate entities to that device through Home Assistant workflows or other integrations
- The integration keeps the configured metadata synchronized with the device registry

The group itself is represented by the config entry, not by a separate Home Assistant device.

## Typical Use Cases

- Prepare device placeholders before the real entities exist
- Create a manual structure for custom or advanced Home Assistant setups
- Keep related virtual devices together under one integration entry
- Maintain consistent device naming and metadata from one place

## Current Model

- Multiple integration entries are allowed
- Each entry acts as an independent group
- A group may be empty
- A group may contain many devices
- The last device in a group can be deleted without deleting the group itself
- Legacy single-device setups are migrated into one initial `General` group entry

## What It Does Not Do

- It does not create entities
- It does not expose sensors, switches, buttons, or services
- It does not currently support `connections` or `configuration_url`
- It does not automatically attach entities to devices for you

## Home Assistant UI Notes

Home Assistant still wraps this integration with some hub-oriented wording in parts of the UI. That wording is a compromise imposed by the platform metadata model, not a perfect description of the internal structure.

The intended model is:

- integration entry = group
- group contains zero or more virtual devices
- each virtual device is a normal Home Assistant device-registry device

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to Integrations
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/PacmanForever/simple_device_creator`
6. Search for "Simple Device Creator" and install

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/PacmanForever/simple_device_creator/releases)
2. Extract the contents to `config/custom_components/simple_device_creator/`
3. Restart Home Assistant

## Configuration

After installation, add the integration through the Home Assistant UI:

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Simple Device Creator"
4. Choose a group name for the entry
5. Optionally add devices with their metadata fields during setup
6. Use the integration options to add, edit, move, delete, or rename later

## Setup Example

Example:

1. Create one entry called `Living Room`
2. Finish setup without devices if you only want the empty group first
3. Open the entry options later
4. Add devices such as `TV Cabinet`, `Ambient Controller`, or `Media Rack`
5. Edit, move, or delete those devices whenever needed

This lets you treat the integration entry as a container and the devices as the items inside that container.

## Features

- Create one config entry that manages multiple virtual devices in Home Assistant's device registry
- Allow empty group entries when you only want to prepare the group first
- Configure device metadata: name, manufacturer, model, software version, and hardware version
- Add, edit, move, and delete devices from the integration options flow, including deleting the last remaining device in a group
- Rename the config entry independently as a device group title
- Keep device names synchronized with renames done from the Home Assistant device registry without changing the group title
- Remove orphaned registry devices when they are no longer present in the config entry data
- Migrate legacy single-device setups into one initial `General` group entry

## Rename Behavior

There are two different names involved:

- The config entry title is the group name
- Each stored device has its own device name

If a user renames one of the managed devices from the Home Assistant device registry UI, that rename is synchronized back only to the matching stored device. The group title is not changed by device renames.

## Moving Devices Between Hubs

Devices can be moved from one hub entry to another from the options flow.

The move is implemented as a registry reassignment, not as a delete-and-recreate operation. This is important because it preserves the same Home Assistant device-registry device instead of replacing it with a new one.

In practical terms, the move flow:

- adds the device to the destination hub entry
- removes the source hub entry from that same device's registry associations
- removes the stored device record from the source hub entry

This is designed to preserve the device identity so existing entity-to-device relationships are not lost just because the device changed hubs.

## Limitations

- Home Assistant's outer UI wording cannot be fully customized by this integration
- Devices created here remain entity-less until something else associates entities with them
- The integration is focused on metadata and registry management, not runtime device communication

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.