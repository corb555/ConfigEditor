# ConfigManager Package

The `ConfigManager` can be used to easily read YML config files and provide an editing front-end with just
10 lines of code and a display format string.
The package provides a structured approach to managing configuration files for applications. 
The application is provided with save, load, set, and get functions and is insulated from the file format.
It includes a base class, `DataManager`, that supports loading, updating, and saving data files. `DataManager` 
uses abstract methods for handling various file formats, enabling data to be loaded into dictionaries or lists 
as needed.  It provides `SettingsWidget` which provides a configurable QT6 UI for editing settings.

The package includes:
- **YAML Configuration Support**: A subclass that implements YAML-specific methods for parsing and saving 
configuration files.
- **Configurable Editing Interface**: A flexible editing window that allows applications to define custom 
widgets and layout structures for easy configuration management.

## Main Contents

### 3. `ConfigFile` 
`ConfigFile` is designed for YAML-based configuration files, providing the tools to load, update, and save 
data. Extending `DataManager`, it includes:
- **YAML Format Compatibility**: Implements methods for parsing and saving YAML files.
- **Change Tracking**: Utilizes inherited functionality for unsaved change tracking, supporting snapshot-based 
- undo actions.
- **Configuration Management**: Designed for structured configuration data, allowing easy integration 
- into applications needing config settings management.

### 4. `SettingsWidget` 
`SettingsWidget` provides a user interface built with QT6 to display and edit settings from a configuration 
file. It features:
- **Dynamic Layout**: Displays settings in a grid layout based on supplied format specifications, with various 
- controls including text fields, combo boxes, and labels.
- **Format Switching**: Supports multiple layouts ("basic" vs "expert" views), adjusting the displayed settings 
- accordingly.
- **Real-Time Syncing**: Updates values in the underlying data dictionary or list as users make changes, ensuring 
- the config file remains in sync.
- **Input Validation**: Validates input against specified rules (regular expressions) and visually 
- highlights invalid entries.
- **Full Redisplay**: Does a full redisplay if specific items change where one field might impact another.
- **Proxy File Touching**: For build system integration, this feature touches a proxy file only when specified 
- fields change, providing more granular dependency tracking.

---
