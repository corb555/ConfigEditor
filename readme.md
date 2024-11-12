# ConfigManager Package

The `ConfigManager` can be used to create a front-end editor for YML files with only 10 lines of code.
The package provides a structured approach to managing configuration files for applications.

## Main Contents

###  `ConfigFile` 
`ConfigFile` provides support for: create, load, and save for YML files.
- **Get / Set**: provides simple get/set for data fields in the YML file.
- **Undo**: Support snapshot-based undo within a session.
- **Proxy File Touch**: For build system integration, this feature touches a proxy file only when specified 
fields change, providing more granular dependency tracking.

###  `SettingsWidget` 
`SettingsWidget` provides a user interface to display and edit settings from a YML configuration 
file. 
- **Configurable Layout**: Displays settings in a grid layout based on supplied format.
- **Widgets**: supports widgets including text edit, line edit, combo box, and label.
- **Data Syncing**: Updates values in the underlying data as users make changes, ensuring 
the config file remains in sync with the UI changes.
- **Input Validation**: Validates input against specified rules (regular expressions) and  
highlights invalid entries.
- **Full Redisplay**: Does a full redisplay if specific items change where one field might impact another.

### `Sample` 
- Provides a sample illustrating the capabilities