# Readme

<img width="622" alt="sample" src="https://github.com/user-attachments/assets/cd9b8b36-a954-40e0-8d62-fc335a2ff8f9">

## Overview

`ConfigEditor` is a Python package for quickly creating simple editors for configuration files. This is useful when
you don't want users to have to use a text editor for your configuration file. This is designed to work with different
format config files. Implementations for YML and JSON config files are included but this can be easily replaced with a
module that can save and load different file formats.

## Features

**SettingsWidget** provides a Widget for displaying and editing fields based on the supplied layout. You
simply list the fields with their config key and the widget you want for them (line_edit, text_edit, label,
combo-box). You can also add a regex for data entry validation. The SettingsWiget and YamlConfig (or JsonConfig) will
read the
config file, display the fields for editing and then save the data.

- **Easy Front-End Creation:** Create a configuration editor for files with a few lines of code.
- **Configurable Layout:** Displays settings in a grid layout based the format you provide.
- **Widget Support:** Supports input widgets, including text edit, line edit, combo box, and label.
- **Input Validation:** Validates input based on specified rules (e.g., regular expressions) and 
highlights invalid entries.
- **Data Syncing:** Synchronizes data values between the UI and the config file, seamlessly using the
  ConfigFile manager described below.
- **Utilizes PyQt6**

**YamlConfig** (or JsonConfig) provides functionality for creating, loading, updating, and saving YAML files.

- **Load / Save / Create** Provides interfaces to load and save YAML files and to create new YAML files.
- **Get / Set Operations:** Provides simple key/value access to data fields in the YAML configuration. Including
scalars (int, float, str), lists, and dictionaries.  _Complex nested hierarchies are not supported._
- **Undo Support:** Keeps a snapshot for each save in session and restores from stack.
- **Granular Dependency Management:** For build system integration, this can be configured to touch a proxy file 
when specified fields change, offering more granular dependency tracking for build systems.

## Installation

To install `ConfigEditor`:

```bash
pip install configeditor
```

### Format Layout

Each line in the format corresponds to a field in the config file with layout
attributes:  
`config_key: (DisplayName, WidgetType, Options, Width)`

- config_Key: The name of the item in the config file
- Display Name: The name to show in the UI for the field.
- Widget Type: The type of input control (e.g., 'line_edit', 'combo', 'read_only').
- Valid Options: Either a regex pattern for field validation (e.g., line_edit), 
       or a list of items for selection (e.g., combo box).
- Field Width: Width of the widget in the UI.

### Sample layout format

```python
formats = {
       "layout1": {
              "TIP": ("Tip Amount", "line_edit", r'^\d{1,2}%?$', 50),
              "DESSERT": ("Dessert", "combo", ["Tiramisu", "Apple Tart", "Cheesecake"], 200),
              "SITES.B": ("Location B", "line_edit", None, 180), "SITES": ("Sites", "line_edit", None, 300),
       },
}
```

### Sample YML file

```yaml
DESSERT: Cheesecake
TIP: 18
SITES:
  A: New Orleans
  B: Boston
  C: Vancouver
  ```

### Sample JSON file

```json
{
       "DESSERT": "Cheesecake",
       "TIP": 18,
       "SITES": {
              "A": "New Orleans",
              "B": "Boston",
              "C": "Vancouver"
       }
}
```

### Sample App

Sample.py is provided to demonstrate the capabilities of `ConfigManager` with a sample YAML file.

## License

`ConfigManager` is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Support

For support or to report an issue, please visit the [issue tracker](https://github.com/corb555/ConfigEditor/issues).

