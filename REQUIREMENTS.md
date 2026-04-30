# Project Requirements

This document outlines the specific requirements for the Simple Device Creator Home Assistant integration project.

## Integration Overview

- **Name**: Simple Device Creator
- **Domain**: simple_device_creator
- **Version**: 0.0.15
- **Home Assistant**: 2024.1.0+

## Functional Requirements

### Core Features
- Create virtual devices without linked entities
- Current UI flow manages multiple devices per integration entry
- Devices can be added, modified, moved between hubs, and deleted after creation through the options flow
- Multiple integration entries are allowed, each acting as an independent device group
- User can later associate entities manually from Home Assistant workflows
- Configuration UI for device creation and editing

### Operating Modes
- Configuration mode: Set up and manage devices through UI
- Runtime mode: Devices appear in HA device registry

### Device Fields (based on HA DeviceInfo)
For each device, the following fields are configurable:
- **name** (required): Display name of the device
- **manufacturer** (optional): Device manufacturer
- **model** (optional): Device model
- **sw_version** (optional): Software version
- **hw_version** (optional): Hardware version

Default values:
- name: "New Device"
- manufacturer: ""
- model: ""
- sw_version: ""
- hw_version: ""

### User Interface
- **Creation Screen**: First collect a group name, then optionally add zero or more devices with all device fields
- **Editing Screen**: Form with editable device fields only (name, manufacturer, model, sw_version, hw_version)
- **Options Flow**: Access device add/edit/move/delete actions and group rename from integration options
- **Empty Entries**: A group entry may exist without any devices and may remain empty after deleting the last device
- **Move Between Hubs**: A stored device may be reassigned from one hub entry to another without replacing the registry device identity
- **Registry Rename Sync**: Renaming a device in HA device settings is synchronized back to the matching stored device only
- **Legacy Migration**: Older single-device entries are consolidated into one initial `General` group entry, which can be renamed later

### Data Storage
- Device data stored in integration entry data under a `devices` list
- Each stored device has a unique internal ID
- The config entry title acts as the user-editable group name
- Persistent across restarts

### API Integration
- **API Endpoint**: None (virtual devices)
- **Authentication**: None required
- **Rate Limits**: None
- **Data Format**: Internal HA device registry
- **Error Handling**: Validation of per-entry device names, legacy migration, and registry synchronization during reload/setup

### Data Collection
- **Update Frequency**: N/A (static devices)
- **Real-time Updates**: N/A
- **Historical Data**: N/A
- **Caching**: Device info stored in HA device registry

## Technical Requirements

### Dependencies
- **Required Packages**: None beyond standard HA requirements
- **Python Version**: 3.11+
- **Platform Requirements**: Any platform supporting HA

### Configuration
- **Required Parameters**: None beyond the device fields entered in the UI config flow
- **Optional Parameters**: None
- **Validation**: Device field validation
- **Security**: No sensitive data stored

### Entities and Platforms
- **Sensors**: None (devices without entities)
- **Binary Sensors**: None
- **Switches/Controls**: None
- **Weather**: None
- **Device Classes**: N/A
- **Events**: None
- **Device Triggers**: None

## Quality Requirements

### Testing
- **Coverage Target**: >95%
- **Unit Tests**: Test config flow, multi-device options flow, setup/unload, migration, pruning, and rename synchronization
- **Component Tests**: Test integration setup and Home Assistant device registry integration
- **Edge Cases**: Duplicate names within one group, empty group entries, deleting the last device, moving a device between hub entries without losing identity, registry rename propagation, orphan registry device cleanup, and legacy consolidation into `General`

### Performance
- **Memory Usage**: Minimal (device configurations)
- **CPU Usage**: Low (no background processing)
- **Network Usage**: None

### Compatibility
- **HA Versions**: 2024.1.0+
- **Python Versions**: 3.11, 3.12
- **Platforms**: All HA supported platforms

## Security Requirements

- **API Key Handling**: None
- **Data Privacy**: No user data collected
- **Network Security**: Not applicable
- **Error Messages**: Generic error messages only

## Deployment Requirements

### HACS Integration
- **Category**: integration
- **Content Root**: false
- **Supported Countries**: All
- **README Rendering**: true

### Release Process
- **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)
- **Changelog**: Update CHANGELOG.md with each release
- **Breaking Changes**: Major version bump

## Maintenance Requirements

### Monitoring
- **Health Checks**: Verify devices are registered
- **Error Reporting**: Log errors during device operations
- **Performance Monitoring**: No specific metrics

### Updates
- **API Changes**: Not applicable
- **HA Compatibility**: Test against new HA versions
- **Dependency Updates**: Update as needed

### Internationalization
- **Supported Languages**: English (base), extensible for others
- **Translation Coverage**: Configuration flow and entity names

---

**Last Updated**: 2026-05-01
**Maintained by**: Project contributors
**Related Documents**:
- `docs/HA_HACS_Integration_Creation_Guide.md`: Setup guide