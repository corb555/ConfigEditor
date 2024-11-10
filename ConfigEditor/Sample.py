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
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from ConfigEditor.config_file import ConfigFile
from ConfigEditor.settings_widget import SettingsWidget


class Sample(QMainWindow):
    """
    This sample loads configuration data from a YAML file, initializes the SettingsWidget
    for displaying and editing specific settings, and provides a save button for committing
    changes back to the configuration file.

    Attributes:
        config (ConfigFile): The configuration file handler.
        settings_widget (SettingsWidget): Widget for displaying and editing settings.
    """

    def __init__(self):
        """Initialize the Sample window, load configuration data, and sets up the UI."""
        super().__init__()

        # Initialize ConfigFile and load configuration data from 'tests/sample.yml'
        config = ConfigFile()
        try:
            config.load("tests/sample.yml")
        except FileNotFoundError as e:
            print(f"Config file not found. {e}")
            sys.exit(1)

        # Define the fields and display formats for the settings widget
        # 'NAMES.@LAYER' retrieves the 'LAYER' field, and displays the NAMES field
        # with that name.  In the sample, this displays NAMES.C
        # 'HILLSHADE2' illustrates using regex to validate input format, such as "-z 3".
        formats = {
            "basic": {
                "NAMES.@LAYER": ("Layer", "read_only", None, 180),
                "HILLSHADE1": ("Shading", "combo", ["-igor", "-alg Horn", "-alg Simple"], 180),
                "HILLSHADE2": ("Z Factor", "line_edit", r'^-z\s+\d+(\s+)?$', 180),
            }
        }

        # Create a SettingsWidget for configuration display and edit, applying format specifications
        settings_widget = SettingsWidget(config, formats, mode="basic")

        # Save button, connected to the SettingsWidget save method to write changes back to file
        save_button = QPushButton("Save")
        save_button.clicked.connect(settings_widget.save)

        # Set up the UI layout with settings widget and save button in a vertical layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(settings_widget)
        layout.addWidget(save_button)
        self.setCentralWidget(central_widget)

        # Display the settings as per format in 'formats' dictionary
        settings_widget.display()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Sample()
    window.show()
    sys.exit(app.exec())
