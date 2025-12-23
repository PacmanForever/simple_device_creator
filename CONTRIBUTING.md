# Contributing to Simple Device Creator

Thank you for your interest in contributing to the Simple Device Creator integration! This document outlines the process for contributing to this project.

## Reporting Issues

- Use the [GitHub Issues](https://github.com/username/simple_device_creator/issues) to report bugs or request features
- Provide detailed information including:
  - Home Assistant version
  - Integration version
  - Steps to reproduce
  - Expected vs actual behavior

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/username/simple_device_creator.git
   cd simple_device_creator
   ```

2. Set up a development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. Run tests:
   ```bash
   python -m pytest tests/
   ```

## Code Standards

- Follow PEP 8 style guidelines
- Use type hints where possible
- Write comprehensive docstrings
- Ensure all code is covered by tests

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests and ensure they pass
5. Update documentation if needed
6. Commit your changes: `git commit -m 'Add some feature'`
7. Push to the branch: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Testing Requirements

- All new code must have unit tests
- Aim for >95% code coverage
- Component tests must verify integration with Home Assistant
- All tests must pass before merging

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to foster an inclusive and welcoming community.