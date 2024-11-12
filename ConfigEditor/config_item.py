from functools import partial
import re
from typing import Union, List, Optional

from PyQt6.QtWidgets import QWidget, QLabel, QComboBox, QLineEdit, QSizePolicy, QTextEdit


class ConfigItem(QWidget):

    def __init__(
            self, config, widget_type, initial_value, options, callback, width=50, key=None,
            text_edit_height=90
    ):
        """
        Creates a widget for displaying and updating data from a config file

        Args:
            widget_type (str): Type of widget to create:
                 ("text_edit", "line_edit", "read_only", "combo","label").
            initial_value (str): Initial value for the widget.
            options : Valid dropdown options for combo box widgets.  Valid regex for edit widgets.
            key (str, optional): Key used to update the data store for this widget
        """
        super().__init__()
        self.error_style = "color: Orange;"
        self.rgx = None  # the regex for validating the text field
        self.widget_type = widget_type
        self.callback = callback  # Called when the widget has been updated.  Allows additional processing by parent
        self.key = key  # The key to link this to the data in the Config file
        self.config = config  # The config file handler

        self._create_widget(widget_type, initial_value, options, width, text_edit_height)

    def _create_widget(
            self, widget_type: str, initial_value: str, options: Optional[Union[List[str], str]],
            width: int, text_edit_height: int
    ):
        """
        Create the specified widget.
        """
        # Create the widget based on type
        if widget_type == "combo":
            self.widget = QComboBox()
            self.widget.addItems(options)
            self.widget.setCurrentText(initial_value)
        elif widget_type == "text_edit":
            self.widget = QTextEdit(str(initial_value))
            self.widget.setFixedHeight(text_edit_height)
            self.rgx = options  # the regex for validating this field
        elif widget_type == "line_edit":
            self.widget = QLineEdit(str(initial_value))
            self.rgx = options  # the regex for validating this field
        elif widget_type == "read_only":
            self.widget = QLineEdit(str(initial_value))
            self.widget.setReadOnly(True)
        elif widget_type == "label":
            self.widget = QLabel()
        else:
            raise TypeError(f"Unsupported widget type: {widget_type}")

        # Set the object name and connect signals for updates.
        # When the widget is updated this will provide the mapping to update the config data
        if "*"  in self.key:
            if widget_type != "read_only":
                print(f"Wildcard items must be read-only: {self.key}")
            else:
                self.widget.setObjectName(self.key)
        else:
            if widget_type != "label":
                self.widget.setObjectName(self.key)
                # Connect widget changed signals
                if isinstance(self.widget, QComboBox):
                    self.widget.currentIndexChanged.connect(
                        partial(self.on_widget_changed, self.widget)
                    )
                else:
                    self.widget.textChanged.connect(partial(self.on_widget_changed, self.widget))

        # Store original style to allow for style reset if needed
        self.widget.setProperty("originalStyle", self.widget.styleSheet())

        # Set widget width
        if width:
            if isinstance(self.widget, QLineEdit):
                self.widget.setFixedWidth(width)  # Use setFixedWidth for QLineEdit
            else:
                self.widget.setMinimumWidth(width)  # Fallback for other widget types

        self.widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def display(self):
        """
        Update widget to display config data
        """
        key, value = None, None
        try:
            if self.widget:
                # Fetch the configuration key from the widget's object name
                key = self.widget.objectName()
                if key:
                    value = self.config.get(key)

                    # Retrieve the corresponding value from the config
                    if value:
                        # Set the widget's display value
                        set_value(self.widget, value)
                    else:
                        print(f"Warning: Key '{key}' not found in configuration data.")
        except Exception as e:
            # Log row, key, and value details if an error occurs
            if not key:
                key = "None"
            if not value:
                value = "None"
            print(
                f"Settings Widget - Error displaying widget at key '{key}', value '{value}': "
                f"{e}"
            )



    def on_widget_changed(self, widget):
        """
        Widget updated: retrieve value, update config data, and validate.

        Args:
            widget (QComboBox |  QTextEdit): The widget whose value changed.
        """

        # todo - ignore_changes is an attribute in SettingsWidget
        # if not self.ignore_changes:
        if True:
            key = widget.objectName()  # Unique key for each setting
            value = get_value(widget)

            # Update config data
            self.config.set(key, value)

            # Validate the new value and set widget styling accordingly
            is_valid = self.validate(value)
            if is_valid:
                self.set_normal_style(widget)
            else:
                self.set_error_style(widget)

            # Allow parent to perform additional processing
            self.callback(key, value)

    def validate(self, value):
        """
        Validate the widget's value against the format's validation regex.

        Args:
            value (str): The value to validate.

        Returns:
            bool: True (valid) if the value matches format regex
        """
        if self.rgx and value:
            # Ensure value meets regex pattern
            return re.match(self.rgx, value) is not None
        else:
            return True

    def set_error_style(self, widget, message=None):
        """
        Set the widget's style to indicate an error.

        Args:
            message (str, optional): An error message to display.
            widget:
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


def get_value(widget):
    """
    Retrieve the value of a widget.

    Args:
        widget (QComboBox or QTextEdit or QLineEdit): The widget to retrieve the value from.

    Returns:
        str: The widget's current value.
    """
    if isinstance(widget, QComboBox):
        return widget.currentText()
    elif isinstance(widget, QTextEdit):
        return widget.toPlainText()
    else:
        return widget.text()


def set_value(widget, value):
    """
    Set the widget's value and validate it.
    If value is invalid, set error style.

    Args:
        widget (QComboBox or QTextEdit or QLineEdit): The widget to set the value for.
        value (str or dict): The new value to set in the widget.
    """
    if isinstance(widget, QComboBox):
        # Set the current text for a QComboBox
        widget.setCurrentText(value)
    elif isinstance(widget, (QLineEdit, QTextEdit)):
        # Format value based on type
        if isinstance(value, dict):
            # Format dictionary nicely
            str_value = ", ".join(f"{key}: {val}" for key, val in value.items())
        else:
            # Ensure value is a string
            str_value = str(value)

        # Set text or plain text based on widget type
        if isinstance(widget, QTextEdit):
            widget.setPlainText(str_value)
        else:
            widget.setText(str_value)
    else:
        raise TypeError(f"Unsupported widget type for setting value. value={value}")
