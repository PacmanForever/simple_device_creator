# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.15] - 2026-05-01

### Changed
- Refactored the integration around group entries that can manage multiple virtual devices.
- Changed device registry rename synchronization so device renames update only the matching stored device, not the entry title.
- Added legacy migration behavior that consolidates older single-device entries into one initial `General` group entry.
- Classified the integration as a hub because that Home Assistant UI wording fits the empty-group model better while keeping config flows working.
- Allowed group entries to remain empty and allowed deleting the last device from an existing group entry.
- Added support for moving a device from one hub entry to another while preserving the underlying device-registry identity.
- Updated config-flow wording to emphasize groups more clearly inside the integration-controlled UI.
- Aligned project documentation with the current multi-device group flow and supported metadata fields.
- Updated Copilot workspace instructions to match the actual Simple Device Creator project.

### Fixed
- Maintained automated test coverage above the 95% target, with current package coverage at 98%.

## [0.0.14] - 2026-01-16

### Fixed
- Fixed integration entry name not updating when renaming device from HA device registry.

## [0.0.13] - 2026-01-15

### Fixed
- Fixed synchronization issue where renaming a device in Home Assistant UI would not update the Integration card name after reload/restart.

## [0.0.12] - 2026-01-15

### Fixed
- Fixed integration title not updating when device name is changed.
- Removed "Modify device information." label from Options Flow.

## [0.0.11] - 2026-01-15

### Fixed
- Fixed device name synchronization between Home Assistant Registry and Integration Options.
- Removed "Delete Device" option from Options Flow (devices must be deleted from HA Registry).

## [Unreleased]

### Added

### Changed

### Fixed

### Deprecated

### Removed

### Security