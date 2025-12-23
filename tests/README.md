# Tests

This directory contains all tests for the Simple Device Creator integration.

## Test Structure

- `unit/`: Unit tests for individual components
- `component/`: Integration tests with Home Assistant

## Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=custom_components.simple_device_creator

# Run specific test types
python -m pytest tests/unit/
python -m pytest tests/component/
```

## Test Requirements

- All tests must pass
- Code coverage >95%
- Tests should be fast and reliable