from functools import partial
from typing import Union, List

from PyQt6.QtWidgets import QWidget, QLabel, QComboBox, QLineEdit, QSizePolicy, QTextEdit

from structured_text import to_text, data_category, get_regex, parse_text


class ItemWidget(QWidget):
    """
    A widget for displaying and editing an item from a configuration file.
    All user edits are validated and synchronized with the configuration data.

    This class supports various widget types for different kinds of fields,
    such as editable text, combo boxes, and read-only labels. It uses the
    `structured_text` module to parse and format text-based representations
    of data structures like dictionaries and lists.

    Attributes:
        config: The configuration file handler object.
        widget_type (str): The type of widget (e.g., "text_edit", "line_edit").
        key (str): Key associated with the field in the configuration data.
        is_valid (bool): Indicates whether the widget's current value is valid.
        value_type (str): Type of the value (e.g., scalar, dict, list).
        error_style (str):  style for indicating an error.
        rgx (str): Regex pattern for validating text fields.
    """

    def __init__(
            self, config, widget_type, initial_value, options, callback, width=50, key=None,
            text_edit_height=90
    ):
        """
        Initialize the ConfigItem widget.

        Args:
            config: Configuration handler to synchronize data.
            widget_type (str): Type of widget to create
                ("text_edit", "line_edit", "read_only", "combo", "label").
            initial_value (str): Initial value to populate the widget.
            options (Union[List[str], str]): Dropdown options for combo boxes or
                regex for validating text fields.
            callback (callable): Function to call when the widget value changes.
            width (int, optional): Fixed width for the widget. Defaults to 50.
            key (str, optional): Key for linking the widget to the configuration data.
            text_edit_height (int, optional): Height for text edit widgets. Defaults to 90.
        """
        super().__init__()
        self.is_valid = False
        self.value_type = None
        self.error_style = "color: Orange;"
        self.rgx = None
        self.widget_type = widget_type
        self.callback = callback
        self.key = key
        self.config = config

        self._create_widget(widget_type, initial_value, options, width, text_edit_height)

    def _create_widget(self, widget_type, initial_value, options, width, text_edit_height):
        """
        Create a specific type of widget based on the provided parameters (private)

        Args:
            widget_type (str): The type of widget to create.
            initial_value (str): The initial value for the widget.
            options (Union[List[str], str], optional): Options or validation regex.
            width (int): Width of the widget.
            text_edit_height (int): Height for text edit widgets.
        """
        if widget_type == "combo":
            self.widget = QComboBox()
            self.widget.addItems(options)
            self.widget.setCurrentText(initial_value)
        elif widget_type == "text_edit":
            self.widget = QTextEdit(str(initial_value))
            self.widget.setFixedHeight(text_edit_height)
            self.rgx = options
        elif widget_type == "line_edit":
            self.widget = QLineEdit(str(initial_value))
            self.rgx = options
        elif widget_type == "read_only":
            self.widget = QLineEdit(str(initial_value))
            self.widget.setReadOnly(True)
        elif widget_type == "label":
            self.widget = QLabel()
        else:
            raise TypeError(f"Unsupported widget type: {widget_type} for {self.key}")

        if widget_type != "label":
            self.widget.setObjectName(self.key)
            if isinstance(self.widget, QComboBox):
                self.widget.currentIndexChanged.connect(
                    partial(self.on_widget_changed, self.widget)
                )
            else:
                self.widget.textChanged.connect(partial(self.on_widget_changed, self.widget))

        self.widget.setProperty("originalStyle", self.widget.styleSheet())
        if isinstance(self.widget, QLineEdit):
            self.widget.setFixedWidth(width)
        else:
            self.widget.setMinimumWidth(width)

        self.widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def display(self):
        """
        Load and display the corresponding value from the configuration data.
        """
        key, val = None, None
        try:
            if self.widget:
                key = self.widget.objectName()
                if key:
                    val = self.config.get(key)
                    if val:
                        if not self.value_type:
                            self.value_type = data_category(val)
                        if self.rgx is None:
                            self.rgx = get_regex(val)
                        self.set_text(self.widget, val)
                    else:
                        print(f"Warning: Key '{key}' not found in configuration data.")
        except Exception as e:
            key = key or "None"
            val = val or "None"
            print(
                f"Error displaying widget for key '{key}', value '{val}': {e}"
            )

    def on_widget_changed(self, widget):
        """
        Handle changes to the widget's value, update the configuration data, validate it,
        and set style appropriately.

        Args:
            widget (QWidget): The widget whose value was changed.
        """
        key = widget.objectName()
        text = get_text(widget)
        self.is_valid = True
        data_value, self.is_valid = parse_text(text, self.value_type, self.rgx)
        if self.is_valid:
            self.config.set(key, data_value)
            self.set_normal_style(widget)
        else:
            self.set_error_style(widget)
        self.callback(key, text)

    def set_error_style(self, widget, message=None):
        """
        Apply an error style to the widget.

        Args:
            widget (QWidget): The widget to style.
            message (str, optional): Optional error message to display.
        """
        if not widget.property("originalStyle"):
            widget.setProperty("originalStyle", widget.styleSheet())
        widget.setStyleSheet(self.error_style)
        if message:
            widget.setText(message)

    def set_normal_style(self, widget):
        """
        Restore the widget's default style.

        Args:
            widget (QWidget): The widget to restore.
        """
        original_style = widget.property("originalStyle")
        widget.setStyleSheet(original_style or "color: Silver;")

    def set_text(self, widget, value):
        """
        Update the widget's text with the provided value.

        Args:
            widget (QWidget): The widget to update.
            value (str or dict): The value to display in the widget.
        """
        if isinstance(widget, QComboBox):
            widget.setCurrentText(value)
        elif isinstance(widget, (QLineEdit, QTextEdit)):
            str_value = to_text(value)
            if isinstance(widget, QTextEdit):
                widget.setPlainText(str_value)
            else:
                widget.setText(str_value)
        else:
            raise TypeError(f"Unsupported widget type for setting value: {type(widget)}")


def get_text(widget):
    """
    Retrieve the text value from a widget.

    Args:
        widget (QWidget): The widget to retrieve the value from.

    Returns:
        str: The current text of the widget.
    """
    if isinstance(widget, QComboBox):
        return widget.currentText()
    elif isinstance(widget, QTextEdit):
        return widget.toPlainText()
    return widget.text()
