
# ConfigEditor

<img width="622" alt="sample" src="https://github.com/user-attachments/assets/cd9b8b36-a954-40e0-8d62-fc335a2ff8f9">

`ConfigEditor` is a Python package for quickly creating a simple editor for a YAML configuration file. This is used when 
you don't want users to have to use a text editor for your YAML configuration file.

**SettingsWidget** provides a Widget for displaying and editing YAML fields based on the supplied layout.

- **Easy Front-End Creation:** Create a configuration editor for YAML files in as few as 10 lines of code.
- **Configurable Layout:** Displays settings in a grid layout based on the provided format.
- **Widget Support:** Supports various input widgets, including text edit, line edit, combo box, and label.
- **Input Validation:** Validates input based on specified rules (e.g., regular expressions) and 
highlights invalid entries.
- **Data Syncing:** Synchronizes data values between the UI and the YAML file, seamlessly using the 
ConfigFile manager described below.
- **Utilizes PyQt6**

**ConfigFile** provides functionality for creating, loading, updating, and saving YAML files.

- **Load / Save / Create** Interfaces to load and save YAML files and to create new YAML files.
- **Get / Set Operations:** Simple access key/value access to data fields in the YAML configuration. Including
scalars (int, float, str), lists, and dictionaries.  _Complex nested hierarchies are not supported._
- **Undo Support:** Keeps a snapshot for each save in session and restores from stack.
- **Granular Dependency Management:** For build system integration, this can be configured to touch a proxy file 
when specified fields change, offering more granular dependency tracking for build systems.


## Installation

To install `ConfigEditor`:

```bash
pip install configeditor
```
### Layout
Each line in 'formats' corresponds to a field in the YAML file, paired with layout
attributes:
- Key: The key to retrieve the item from the YAML data
- Display Name: The name to show in the UI for the field.
- Widget Type: The type of input control (e.g., 'line_edit', 'combo', 'read_only').
- Valid Options: Either a regex pattern for field validation (e.g., line_edit), 
       or a list of items for selection (e.g., combo box).
- Field Width: Width of the widget in the UI.

### Sample

Sample.py is provided to demonstrate the capabilities and setup of `ConfigManager` with a sample configuration file. 

## License

`ConfigManager` is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Support

For support or to report an issue, please visit the [issue tracker](https://github.com/corb555/ConfigEditor/issues).

