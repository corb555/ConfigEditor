#  Copyright (c) 2024. Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated
#  documentation files (the “Software”), to deal in the Software without restriction, including
#  without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
#  Software, and to permit
#  persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or
#  substantial portions of the
#  Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
#  BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
#  EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
#  CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
from functools import partial
import os
import re

from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QComboBox, QLineEdit, QSpacerItem, \
    QSizePolicy, QTextEdit


class SettingsWidget(QWidget):
    """Provides a  user interface for editing settings from a config file. Reads and updates
    settings from a Dictionary and displays widgets in a grid layout based on a
    supplied format.

    Key Functionalities:
    - Displays settings based on formats which define the layout, type of
    control (text fields, combo boxes, and labels), and dictionary key.
    - Supports switching between multiple formats (e.g., "basic" vs "expert" format)
    - Handles changes made to widgets by syncing the updated values back to the  Dict.
    - Validates user input according to provided rules (regular expressions) and highlights
      the entry if there is an error.
    - Supports full redisplay if specified configuration keys change.
    - Supports proxy file touch for specified configuration keys, aiding build system dependency
     management by ensuring that changes to certain keys touch a proxy file and trigger build
     system dependency checks.

    Attributes:
        config (Config): The configuration object that holds the settings in a Dict.  Needs to
        support key/value get, set, load and save.
        formats (dict): A dictionary that defines display formats and input validation rules. Can
        contain multiple formats (e.g., "expert" mode, "basic" mode) for the same data.
        ignore_changes (bool): A flag to temporarily disable change detection when updating widgets.
        is_loaded (bool): A flag indicating whether the settings have been loaded into the UI.
        validation_format_key (str): The format used for input validation (default is the first
        format in the dictionary).
        error_style (str): The style for errors (default is "color: Orange;").
        redisplay_keys (list of str): A list of configuration keys that trigger a full redisplay
            of the UI when modified.
        proxy_update_keys (list of str): A list of configuration key prefixes that, when changed,
            force a touch to the dependency proxy file.
        dependency_proxy (str, optional): A file path for a proxy file that is touched when
            settings in proxy_update_keys change.  Used to assist build system dependency
            management.

    Format line:
                dictionary_key: (DisplayName, Type, Options, Size)

    Sample format:
        formats = {
            "expert": {
                "NAMES.*": ("Names", "read_only", None, 180),
                "NAMES.@LAYER": ("Layer", "read_only", None, 180),
                "HILLSHADE1": ("Shading", "combo", ["-igor", '-alg Horn', '-alg '], 180),
                "HILLSHADE2": ("Z Factor", "text_edit", r'^w+$', 180),
                }
            }

      NAMES.@LAYER reads the value of @LAYER and uses that appended to NAMES.
      NAMES.* returns a list of all items under NAMES
    """

    def __init__(
            self, config, formats, mode, redisplay_keys=None, proxy_update_keys=None
    ):
        """
        Initialize the settings widget.

        Args:
            config (Config): Configuration object to store settings.
            formats (dict): Display formats for different modes.
            mode (str): Used to select between multiple formats
            redisplay_keys(List): Updates to these keys trigger full redisplay
            proxy_update_keys(List) Updates to these keys trigger proxy touch
        """
        super().__init__()
        self.config = config
        self.formats = formats
        self.grid_layout = QGridLayout(self)
        self.ignore_changes = False
        self.is_loaded = False
        self.mode = mode
        # Validation defaults to the first format in formats
        self.validation_format_key = next(iter(self.formats))
        self.error_style = "color: Orange;"
        self.redisplay_keys = redisplay_keys  # Keys that trigger full UI redisplay

        self.dependency_proxy = None  # Proxy file for dependencies
        self.proxy_update_keys = proxy_update_keys  # Keys that trigger proxy updates

    def setup_ui(self):
        """
        Create and arrange widgets based on the display format.
        """
        self.grid_layout.setSpacing(10)
        self.clear_layout()
        display_format = self.formats[self.mode]

        for row, (key, (label_text, widget_type, options, width)) in enumerate(
                display_format.items()
        ):
            widget = self.create_widget(widget_type, "", options, key)

            if widget:
                label = QLabel(label_text)
                label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                self.grid_layout.addWidget(label, row, 0)
                self.grid_layout.addWidget(widget, row, 1)

                if width:
                    widget.setMinimumWidth(width)

                widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

                self.grid_layout.addItem(
                    QSpacerItem(1, 1, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum),
                    row, 2
                )

        self.grid_layout.addItem(
            QSpacerItem(1, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum),
            self.grid_layout.rowCount(), 0, 1, 3
        )

    def create_widget(self, widget_type, initial_value, options=None, key=None):
        """
        Create a widget based on specified type.

        Args:
            widget_type (str): Type of widget to create ("text_edit", "read_only", "combo",
            "label").
            initial_value (str): Initial value for the widget.
            options (list, optional): Options for combo box widgets.
            key (str, optional): Name for the widget. Used to update the data store

        Returns:
            QWidget: The created widget.
        """
        self.validation_format = self.formats[self.validation_format_key]

        # Create the widget based on type
        if widget_type == "combo":
            widget = QComboBox()
            widget.addItems(options)
            widget.setCurrentText(initial_value)
        elif widget_type == "text_edit":
            widget = QTextEdit(str(initial_value))
            widget.setFixedHeight(90)
        elif widget_type == "label":
            widget = QLabel(str(initial_value))
        elif widget_type == "line_edit":
            widget = QLineEdit(str(initial_value))
        elif widget_type == "read_only":
            widget = QLineEdit(str(initial_value))
            widget.setReadOnly(True)
        else:
            raise TypeError(f"Unsupported widget type: {widget_type}")

        # Set object name for non-label widgets and connect signals to allow data update
        if widget_type != "label":
            widget.setObjectName(key)
            self.connect_signals(widget)

        # Store original style to allow for style reset if needed
        widget.setProperty("originalStyle", widget.styleSheet())

        return widget

    def _set_value(self, widget, key, value):
        """
        Update the widget's value and validate it against the format.
        If value is invalid, set error style.

        Args:
            widget (QWidget): The widget to set the value for.
            key (str): The key associated with the widget.
            value (str or dict): The new value to set in the widget. Could be a dict when using
            wildcards.
        """
        if isinstance(widget, QComboBox):
            widget.setCurrentText(value)
        elif isinstance(widget, QLineEdit) or isinstance(widget, QTextEdit):
            # Handle wildcard keys (e.g., name.*)
            if ".*" in key:
                # Convert dict items to a string for display
                dict_as_string = ", ".join(f"{k}: {v}" for k, v in value)
                if isinstance(widget, QTextEdit):
                    widget.setPlainText(dict_as_string)
                else:
                    widget.setText(dict_as_string)
            else:
                # Set value directly
                if isinstance(widget, QTextEdit):
                    widget.setPlainText(value)
                else:
                    widget.setText(value)

            # Validate the value
            is_valid = self.validate(key, value)
            if is_valid:
                self.set_normal_style(widget)
            else:
                self.set_error_style(widget)
        else:
            raise TypeError(f"Unsupported widget type for setting value.  key={key} value={value}")

    def _get_value(self, widget):
        """
        Retrieve the value from a widget.

        Args:
            widget (QWidget): The widget to retrieve the value from.

        Returns:
            str: The widget's current value.
        """
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QTextEdit):
            return widget.toPlainText()
        else:
            return widget.text()

    def connect_signals(self, widget):
        """
        Connect signals for tracking widget updates.

        Args:
            widget (QWidget): The widget to connect signals for.

        Raises:
            TypeError: If the widget type is unsupported.
        """
        if isinstance(widget, QComboBox):
            widget.currentIndexChanged.connect(partial(self.on_widget_changed, widget))
        else:
            widget.textChanged.connect(partial(self.on_widget_changed, widget))

    def validate(self, key, value):
        """
        Validate the widget's value against the format's validation regex.

        Args:
            key (str): The key associated with the widget.
            value (str): The value to validate.

        Returns:
            bool: True (valid) if the value matches format regex
        """
        if key in self.validation_format:
            _, widget_type, options, _ = self.validation_format[key]
            if (
                    widget_type == "text_edit" or widget_type == "line_edit" or widget_type ==
                    "read_only") and options and value:
                return re.match(options, value) is not None
        return True

    def on_widget_changed(self, widget):
        """
        Handle value changes in widgets: update config data, validate, and manage UI state.

        Args:
            widget (QWidget): The widget whose value changed.
        """
        if not self.ignore_changes:
            key = widget.objectName()  # Unique key for each setting
            value = self._get_value(widget)

            self.update_value(key, value)
            # Validate the new value and adjust widget styling accordingly
            is_valid = self.validate(key, value)
            if is_valid:
                self.set_normal_style(widget)
            else:
                self.set_error_style(widget)

    def update_value(self, key, value):
        if key:
            # Update the configuration with the new value
            self.config.set(key, value)

            # Force full redisplay if the key is in the redisplay list
            if self.redisplay_keys is not None:
                if key in self.redisplay_keys:
                    self.display()

            # Trigger proxy update if the key matches any of the proxy update keys
            if self.proxy_update_keys is not None:
                print(f"update key={key} value={value}")
                print(f"filter={self.proxy_update_keys}")
                if any(
                        key.startswith(prefix) for prefix in self.proxy_update_keys
                ) and self.dependency_proxy:
                    print(f"touch {self.dependency_proxy}")
                    touch_file(self.dependency_proxy)

    def display(self):
        """
        Synch data from the Config object to the display widgets
        """
        self.ignore_changes = True
        if not self.grid_layout.count():
            self.setup_ui()

        for row in range(self.grid_layout.rowCount() - 1):
            widget_item = self.grid_layout.itemAtPosition(row, 1)
            if widget_item:
                widget = widget_item.widget()
                if widget:
                    key = widget.objectName()
                    if key:
                        value = self.config.get(key, "")
                        self._set_value(widget, key, value)

        self.ignore_changes = False
        self.is_loaded = True

    def save(self):
        """
        Save the current settings from the UI to the configuration file using config.save()
        Don't overwrite the storage if we haven't yet loaded from it
        """
        if self.is_loaded:
            self.config.save()

    def clear_layout(self):
        self._clear_layout(self.grid_layout)

    def _clear_layout(self, layout):
        """
        Remove all items from a layout

        Args:
            layout (QLayout): The layout to clear.
        """
        self.is_loaded = False
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()
            if widget:
                widget.deleteLater()

            nested_layout = item.layout()
            if nested_layout:
                self._clear_layout(nested_layout)

    def set_error_style(self, widget, message=None):
        """
        Set the widget's style to indicate an error.

        Args:
            widget (QWidget): The widget to style.
            message (str, optional): An error message to display.
        """
        if not widget.property("originalStyle"):
            widget.setProperty("originalStyle", widget.styleSheet())

        widget.setStyleSheet(self.error_style)
        if message:
            widget.setText(message)

    def set_normal_style(self, widget):
        """
        Restore the widget's normal style.

        Args:
            widget (QWidget): The widget to restore.
        """
        original_style = widget.property("originalStyle")
        if original_style:
            widget.setStyleSheet(original_style)
        else:
            widget.setStyleSheet("color: Silver;")


def touch_file(filename):
    """
    Set the file's modification and access time to the current time.

    Args:
        filename (str): Path to the file.
    """
    with open(filename, 'a'):
        print(f"touch_file {filename}")
        os.utime(filename, None)
