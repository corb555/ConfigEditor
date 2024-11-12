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
    A sample application that loads configuration data from a YAML file, initializes
    the SettingsWidget for displaying and editing settings, and provides a save button
    to save changes back to the YAML file.
    """

    def __init__(self):
        """
        Define the 'formats' dictionary to specify the display format for SettingsWidget.

        - Each key in 'formats' corresponds to a field in the YAML file, paired with layout
        attributes:
            a) Display Name: The name shown in the UI for the setting.
            b) Widget Type: The type of input control (e.g., 'line_edit', 'combo', 'read_only').
            c) Valid Options: Either a regex pattern for field validation (e.g., line_edit), 
               or a list of items for selection (e.g., combo box).
            d) Field Width: Width of the widget in the UI.

        Format lines below:
            - "LABEL1" - Displays a label
            - "TIP" - Creates a line_edit widget. The field highlights if the entered value  
            doesn't match the regex validation, e.g. one or two decimals and optional "%"
            - "DESSERT" - Displays a combo box to select a dessert item.
            - "SITES.B" - A read-only field displaying the value of "B" under the SITES dictionary.
            - "SITES.@HOME" - Retrieves the 'HOME' field and uses that as a subkey. Retrieves
            SITES.C in
            this example.
            - "SITES.*" - Displays all the sub-items under the SITES dictionary.
        """

        formats = {
            "layout1": {
                "LABEL1": ("Menu", "label", None, 400),
                "TIP": ("Tip Amount", "line_edit", r'^\d{1,2}%?$', 50),
                "DESSERT": ("Dessert", "combo", ["Tiramisu", "Apple Tart", "Cheesecake"], 200),
                "LABEL2": (" ", "label", None, 400),
                "SITES.*": ("Locations", "read_only", None, 300),
                "HOME": ("Home", "combo", ["A", "B", "C"], 200),
                "SITES.@HOME": ("Home Location", "read_only", None, 180),
                "SITES.B": ("Location B", "read_only", None, 180),
            }
        }

        super().__init__()

        # Load YML configuration data from 'tests/sample.yml'.
        config = ConfigFile()
        config.load("tests/sample.yml")

        # Create a SettingsWidget and configure the display/edit fields based on 'formats'.
        # Data is linked between the widgets and the corresponding fields in the config file
        # A change to "HOME" will force a full redisplay including the "SITES.@HOME" item
        settings_widget1 = SettingsWidget(config, formats, mode="layout1", redisplay_keys=["HOME"])

        # Link Save button to SettingsWidget.save to commit changes back to YAML file.
        save_button1 = QPushButton("Save")
        save_button1.clicked.connect(settings_widget1.save)

        # Set up the display with the settings widget and save button
        central_widget = QWidget()
        left_layout = QVBoxLayout(central_widget)
        left_layout.addWidget(settings_widget1)
        left_layout.addWidget(save_button1)
        self.setCentralWidget(central_widget)

        # Display the settings from the config file and allow editing
        settings_widget1.display()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Sample()
    window.show()
    sys.exit(app.exec())
