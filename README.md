# Simple Device Creator

[![Unit Tests](https://github.com/username/simple_device_creator/actions/workflows/tests_unit.yml/badge.svg)](https://github.com/username/simple_device_creator/actions/workflows/tests_unit.yml)
[![Component Tests](https://github.com/username/simple_device_creator/actions/workflows/tests_component.yml/badge.svg)](https://github.com/username/simple_device_creator/actions/workflows/tests_component.yml)
[![Validate HACS](https://github.com/username/simple_device_creator/actions/workflows/validate_hacs.yml/badge.svg)](https://github.com/username/simple_device_creator/actions/workflows/validate_hacs.yml)
[![Validate Hassfest](https://github.com/username/simple_device_creator/actions/workflows/validate_hassfest.yml/badge.svg)](https://github.com/username/simple_device_creator/actions/workflows/validate_hassfest.yml)

A Home Assistant integration that allows users to create simple virtual devices for testing and development purposes.

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to Integrations
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/username/simple_device_creator`
6. Search for "Simple Device Creator" and install

### Manual Installation

1. Download the latest release from [GitHub Releases](https://github.com/username/simple_device_creator/releases)
2. Extract the contents to `config/custom_components/simple_device_creator/`
3. Restart Home Assistant

## Configuration

After installation, add the integration through the Home Assistant UI:

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Simple Device Creator"
4. Follow the configuration steps

## Features

- Create virtual sensors with customizable values
- Support for different data types (temperature, humidity, etc.)
- Easy configuration through the UI
- Real-time value updates

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.