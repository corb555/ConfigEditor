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

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout

from ConfigEditor.config_file import ConfigFile, rgx_starts, rgx_multiple_switches, rgx_token_suffix
from ConfigEditor.settings_widget import SettingsWidget

"""
A sample application that loads configuration data from a YAML file, initializes
the SettingsWidget for displaying and editing settings, and provides a save button
to save changes back to the YAML file.
"""

"""
Define the 'formats'  to specify the display format for SettingsWidget.

Format lines below:
    - "LABEL1" - Displays a label
    - "TIP" - Creates a line_edit widget. The field highlights if the entered value  
    doesn't match the regex validation, e.g. one or two decimals and optional "%"
    - "DESSERT" - Displays a combo box to select a dessert item.
    - "SITES.B" - A read-only field displaying the value of "B" under the SITES dictionary.
    - "SITES.@HOME" - Retrieves the 'HOME' field and uses that as a subkey. Retrieves
    SITES.C in
    this example.
    - "SITES" - Displays all the sub-items under the SITES dictionary.
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load YAML configuration data from 'tests/sample.yml'.
    config = ConfigFile()
    config.load("tests/sample.yml")

    # Create the UI layout for the fields in the YML file.  Each line is a row in the UI
    formats = {
        "layout1": {
            "LABEL1": ("Menu", "label", None, 400),
            "TIP": ("Tip Amount", "line_edit", r'^\d{1,2}%?$', 50),
            "DESSERT": ("Dessert", "combo", ["Tiramisu", "Apple Tart", "Cheesecake"], 200),
            "LABEL2": (" ", "label", None, 400),
            "HOME": ("Home", "combo", ["A", "B", "C"], 200),
            "SITES.@HOME": ("Home Location", "read_only", None, 180),
            "SITES.B": ("Location B", "read_only", None, 180),
            "SITES": ("Sites", "line_edit", None, 300),
            "people": ("People", "line_edit", None, 300),
        },
    }

    # Create  settings widget to display and edit the YAML settings
    settings_widget = SettingsWidget(config, formats,"layout1",["HOME"])

    # Link Save button to SettingsWidget.save to commit changes back to YAML file.
    save_button = QPushButton("Save")
    save_button.clicked.connect(settings_widget.save)

    # Link Undo button to SettingsWidget.undo to undo changes
    undo_button = QPushButton("Undo")
    undo_button.clicked.connect(settings_widget.undo)

    # Set up the display with the settings widget and save button
    window = QWidget()

    button_layout = QHBoxLayout()
    button_layout.addWidget(save_button)
    button_layout.addWidget(undo_button)

    layout = QVBoxLayout()
    layout.addWidget(settings_widget)
    layout.addLayout(button_layout)
    window.setLayout(layout)

    # Display the settings from the config file and allow editing
    settings_widget.display()

    window.show()
    sys.exit(app.exec())
