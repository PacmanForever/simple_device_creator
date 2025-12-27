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

A Home Assistant integration that allows users to create custom and empty devices.

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
4. Follow the configuration steps

## Features

- Create custom device entries in Home Assistant's device registry
- Configure device properties (name, manufacturer, model, versions, configuration URL)
- Add device connections (MAC addresses, IP addresses, etc.)
- Manage devices through an intuitive configuration flow
- Support for device creation, editing, and deletion
- Empty device containers ready for integration with other components

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.