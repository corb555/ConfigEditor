
# ConfigManager

`ConfigManager` is a Python package designed to provide an easy-to-use interface for managing YAML configuration files, with a focus on creating front-end editors with minimal code. This package includes features for basic configuration management, user-friendly editing, and seamless integration with build systems. **Note:** YAML files containing lists are not currently supported.

## Features

- **Easy Front-End Creation:** Create a configuration editor for YAML files in as few as 10 lines of code.
- **Structured Configuration Management:** Simplify management of configuration files with built-in support for essential operations like saving, loading, and editing.
- **Undo & Dependency Tracking:** Manage configuration changes within a session and track dependencies with file touch support for efficient build integration.

## Installation

To install `ConfigManager`, you can use `pip`:

```bash
pip install configmanager
```

## Usage

### Quick Start

```python
from configmanager import ConfigFile, SettingsWidget

# Load or create a configuration file
config = ConfigFile("path/to/config.yml")

# Create a settings editor widget
widget = SettingsWidget(config)
widget.show()
```

This example demonstrates loading a YAML configuration file and creating a GUI widget for editing its values.

## Main Components

### `ConfigFile`

`ConfigFile` provides functionality for creating, loading, and saving YAML files, along with essential utilities for configuration management.

- **Get / Set Operations:** Simplify accessing and modifying data fields in the YAML configuration.
- **Undo Support:** Snapshot-based undo within a session, allowing changes to be rolled back if necessary.
- **Proxy File Touch:** For build system integration, touches a proxy file only when specified fields change, offering precise dependency tracking.

### `SettingsWidget`

`SettingsWidget` provides a GUI for displaying and editing YAML file settings in a structured layout.

- **Configurable Layout:** Displays settings in a grid layout based on the provided format.
- **Widget Support:** Supports various input widgets, including text edit, line edit, combo box, and label.
- **Data Syncing:** Synchronizes data values between the UI and the YAML file, ensuring consistency.
- **Input Validation:** Validates input based on specified rules (e.g., regular expressions) and highlights invalid entries.
- **Dynamic Redisplay:** Automatically refreshes fields in cases where changes in one field affect others.

### `Sample`

A sample file is provided to demonstrate the capabilities and setup of `ConfigManager` with a sample configuration file. The sample includes usage examples of both `ConfigFile` and `SettingsWidget`.


## License

`ConfigManager` is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Support

For support or to report an issue, please visit the [issue tracker](https://github.com/yourusername/configmanager/issues).

