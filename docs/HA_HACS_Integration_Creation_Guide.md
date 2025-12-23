# Home Assistant HACS Integration Creation Guide

This guide provides the generic steps to set up a custom integration project for Home Assistant (HA) compatible with HACS (Home Assistant Community Store), based on the structure and configurations of an existing project. It only covers aspects related to GitHub, HA, and HACS, without details on the integration's internal functionality.

## Required Files and Documents

Here's a comprehensive list of all files and documents that need to be created for a complete HA integration project:

### Core Integration Files
- **`custom_components/integration_name/__init__.py`**: Main integration entry point
- **`custom_components/integration_name/manifest.json`**: HA integration manifest (see section 2)
- **`custom_components/integration_name/config_flow.py`**: Configuration flow implementation
- **`custom_components/integration_name/coordinator.py`**: Data coordinator for API calls
- **`custom_components/integration_name/sensor.py`**: Sensor entities
- **`custom_components/integration_name/binary_sensor.py`**: Binary sensor entities (if needed)
- **`custom_components/integration_name/weather.py`**: Weather entity (if applicable)
- **`custom_components/integration_name/strings.json`**: Translation strings
- **`custom_components/integration_name/const.py`**: Constants and configuration

### Configuration and Metadata
- **`hacs.json`**: HACS configuration (see section 3)
- **`requirements.txt`**: Runtime dependencies
- **`requirements-test.txt`**: Test dependencies
- **`REQUIREMENTS_TEMPLATE.md`**: Detailed project requirements (for AI assistants)
- **`LICENSE`**: GPL-3.0 license file

### GitHub Actions Workflows
- **`.github/workflows/tests_unit.yml`**: Unit tests workflow
- **`.github/workflows/tests_component.yml`**: Component tests workflow
- **`.github/workflows/validate_hacs.yml`**: HACS validation workflow
- **`.github/workflows/validate_hassfest.yml`**: HA validation workflow
- **`.github/workflows/daily_compatibility.yml`**: Daily compatibility checks

### Documentation
- **`README.md`**: Main project documentation in English (installation, features, badges)
- **`CONTRIBUTING.md`**: Contribution guidelines in English (reporting issues, PR process, code standards)
- **`CHANGELOG.md`**: Version history in English (release notes and changes)
- **`QUALITY.md`**: Quality guidelines in English (testing requirements, standards)
- **`REQUIREMENTS.md`**: Dependencies documentation in English (optional but recommended)

### Tests
- **`tests/__init__.py`**: Test package initialization
- **`tests/conftest.py`**: Test configuration and fixtures
- **`tests/unit/`**: Unit test files
- **`tests/component/`**: Component test files
- **`tests/README.md`**: Test documentation

### Release and Automation
- **`release_to_github.py`**: Release automation script
- **`push_release.py`**: Push release script
- **`run_tests.py`**: Local test runner
- **`pytest.ini`**: Pytest configuration

## 1. GitHub Repository Setup

### Create the Repository
- Create a new public repository on GitHub with a descriptive name (e.g., `integration_name`).
- Add a clear description and an initial README.
- Enable GitHub Actions (Settings > Actions > General > Allow all actions).

### Basic Project Structure
Organize the repository with the following structure:

```
/
├── .github/
│   └── workflows/          # GitHub Actions workflows
├── custom_components/
│   └── integration_name/   # Integration code
│       ├── __init__.py
│       ├── manifest.json
│       ├── ...             # Other integration files
├── tests/                  # Tests
├── hacs.json               # HACS configuration
├── requirements.txt         # Dependencies
├── requirements-test.txt    # Test dependencies
├── README.md                # Main documentation
├── CONTRIBUTING.md          # Contribution guide
├── LICENSE                  # License (GPLv3 recommended)
└── ...                      # Other files (CHANGELOG, etc.)
```

### Essential Files
- **README.md**: Main documentation with installation, features, etc.
- **CONTRIBUTING.md**: Guide for contributors with code standards and tests.
- **LICENSE**: Open-source license (GPLv3 for HA compatibility).
- **requirements.txt**: Integration dependencies.
- **requirements-test.txt**: Dependencies for tests (pytest, etc.).

## 2. Home Assistant Configuration

### Integration Manifest
Create `custom_components/integration_name/manifest.json` with the following generic structure:

```json
{
  "domain": "integration_name",
  "name": "Integration Name",
  "codeowners": ["@github_username"],
  "config_flow": true,
  "documentation": "https://github.com/username/integration_name",
  "integration_type": "hub",
  "iot_class": "cloud_polling",
  "issue_tracker": "https://github.com/username/integration_name/issues",
  "requirements": ["dependency>=version"],
  "version": "1.0.0"
}
```

- **domain**: Unique identifier for the integration.
- **name**: Visible name in HA.
- **codeowners**: Code maintainers.
- **config_flow**: Enables configuration flow.
- **documentation**: Repository URL.
- **integration_type**: Integration type (hub, device, etc.).
- **iot_class**: IoT class (cloud_polling, local_polling, etc.).
- **requirements**: Required dependencies.
- **version**: Current version (must match Git tags).

### Validation with Hassfest
Set up GitHub Actions to validate the manifest with Hassfest (official HA tool).

## 3. HACS Configuration

### hacs.json File
Create `hacs.json` at the repository root:

```json
{
  "name": "Integration Name",
  "content_in_root": false,
  "render_readme": true,
  "homeassistant": "2024.1.0"
}
```

- **name**: Visible name in HACS.
- **content_in_root**: false (content is in custom_components/).
- **render_readme**: true to display README in HACS.
- **homeassistant**: Minimum required version.

### HACS Validation
Set up GitHub Actions to validate HACS compatibility.

## 4. GitHub Actions (CI/CD)

### Test Types
Set up comprehensive testing with the following types:

- **Unit Tests** (`tests/unit/`): Test individual functions, classes, and modules in isolation without HA dependencies.
- **Component Tests** (`tests/component/`): Test the integration within HA environment, including configuration flows, entities, and real HA interactions.

Aim for **>95% code coverage** (Home Assistant Silver Level requirement).

### Recommended Workflows
Create workflows in `.github/workflows/` for:

- **Unit Tests**: `tests_unit.yml` - Runs unit tests with coverage
- **Component Tests**: `tests_component.yml` - Runs component tests with coverage  
- **HACS Validation**: `validate_hacs.yml` - Validates HACS compatibility
- **Hassfest Validation**: `validate_hassfest.yml` - Validates HA manifest and structure
- **Daily Compatibility**: `daily_compatibility.yml` - Checks compatibility with latest HA stable/beta

### Workflow Configuration
Use these triggers for all workflows:
- `push` to `main` branch
- `pull_request` to `main` branch  
- `workflow_dispatch` for manual runs

For daily compatibility, add:
```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6:00 AM UTC
  workflow_dispatch:
```

Test against multiple Python versions (e.g., 3.11, 3.12) using matrix strategy.

### Example Unit Tests Workflow
```yaml
name: Unit Tests
on:
  workflow_dispatch:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: |
          python -m pip install --upgrade pip
          pip install homeassistant
          pip install -r requirements-test.txt
      - run: python -m pytest tests/unit --cov=custom_components.integration_name --cov-report=term -v
```

### Example Component Tests Workflow
```yaml
name: Component Tests
on:
  workflow_dispatch:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: |
          python -m pip install --upgrade pip
          pip install homeassistant
          pip install -r requirements-test.txt
      - run: python -m pytest tests/component --cov=custom_components.integration_name --cov-report=term -v
```

### Validation Workflows
```yaml
# validate_hacs.yml
name: HACS Validation Tests
on: [push, pull_request, workflow_dispatch]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hacs/action@main
        with:
          category: integration

# validate_hassfest.yml  
name: HA Validation Tests
on: [push, pull_request, workflow_dispatch]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: home-assistant/actions/hassfest@master
```

### Badges
Add badges to README to show workflow status:

```markdown
[![Unit Tests](https://github.com/username/repo/actions/workflows/tests_unit.yml/badge.svg)](https://github.com/username/repo/actions/workflows/tests_unit.yml)
[![Component Tests](https://github.com/username/repo/actions/workflows/tests_component.yml/badge.svg)](https://github.com/username/repo/actions/workflows/tests_component.yml)
[![Validate HACS](https://github.com/username/repo/actions/workflows/validate_hacs.yml/badge.svg)](https://github.com/username/repo/actions/workflows/validate_hacs.yml)
[![Validate Hassfest](https://github.com/username/repo/actions/workflows/validate_hassfest.yml/badge.svg)](https://github.com/username/repo/actions/workflows/validate_hassfest.yml)
```

## 5. Release Process

### Versioning
- Use semantic versioning (e.g., 1.0.0).
- Update version in `manifest.json` before each release.
- Create Git tags for versions (e.g., `v1.0.0`).

### Release Scripts
Create Python scripts to automate releases:

- `release_to_github.py`: Create tag and push to GitHub.
- `push_release.py`: Manage release pushes.

Basic example:

```python
import subprocess

# Create tag
subprocess.run(['git', 'tag', '-a', 'v1.0.0', '-m', 'Release v1.0.0'])

# Push branch and tag
subprocess.run(['git', 'push', 'origin', 'main'])
subprocess.run(['git', 'push', 'origin', 'v1.0.0'])
```

### GitHub Releases
- Create manual releases on GitHub with change notes.
- Use CHANGELOG.md to document changes.

## 6. Documentation

### README.md
Create a comprehensive README.md that includes:
- Project title and description
- Installation instructions (HACS and manual)
- Main features and capabilities
- Status badges (tests, coverage, HACS validation)
- Configuration examples
- Links to documentation and issue tracker
- License information

### CONTRIBUTING.md
Define clear contribution guidelines:
- How to report bugs and request features
- Development setup and coding standards (PEP 8)
- Pull request process and review requirements
- Testing requirements (>95% coverage)
- Code of conduct

### CHANGELOG.md
Maintain a version history:
- Release notes for each version
- Bug fixes, new features, and breaking changes
- Migration guides when applicable
- Format: Keep a Date - Version - Changes structure

### QUALITY.md
Document quality standards:
- Testing requirements (unit, component, coverage)
- Code review checklist
- Performance and security guidelines
- Compatibility requirements (Python versions, HA versions)

### Additional Documentation (Optional)
- **`REQUIREMENTS.md`**: Detailed dependency explanations
- **`FUTURE_PLANS.md`**: Roadmap and planned features
- **`RELEASE_NOTES.md`**: Detailed release information
- **`.ai_instructions.md`**: AI assistant guidelines (recommended for complex projects)

### AI Assistant Integration
Create a `.ai_instructions.md` file to guide AI assistants:

- **Template available**: Use the provided `.ai_instructions.md` as a starting point
- **Customize for project**: Replace placeholders with actual integration details
- **Separate requirements**: Use `PROJECT_REQUIREMENTS.md` for detailed specifications
- **Update as needed**: Modify when requirements or processes change
- **Include project context**: Add specific API docs, domain names, and requirements

This helps AI assistants understand the codebase and maintain consistency.

## 8. Best Practices

- **Quality**: Aim for Home Assistant Silver Level (>95% code coverage across unit and component tests).
- **Tests**: Write comprehensive tests for all functionalities - unit tests for isolated logic, component tests for HA integration.
- **CI/CD**: Keep all workflows green, test against multiple Python versions (3.11, 3.12).
- **Validation**: Ensure HACS and Hassfest validations pass.
- **Compatibility**: Run daily checks against latest HA stable/beta releases.
- **Security**: Do not expose API keys in commits.
- **Community**: Accept contributions and keep issues open.

This guide serves as a template for creating similar integrations. Adapt names and details according to your specific project.