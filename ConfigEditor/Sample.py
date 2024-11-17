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

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

from ConfigEditor.config_file import ConfigFile, rgx_starts, rgx_multiple_switches, rgx_token_suffix
from ConfigEditor.settings_widget import SettingsWidget

"""
A sample application that loads configuration data from a YAML file, initializes
the SettingsWidget for displaying and editing settings, and provides a save button
to save changes back to the YAML file.
"""

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
    - "SITES" - Displays all the sub-items under the SITES dictionary.
"""

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load YAML configuration data from 'tests/sample.yml'.
    config = ConfigFile()
    config.load("tests/USA_relief.cfg")

    formats1 = {
        "layout1": {
            "LABEL1": ("Menu", "label", None, 400),
            "TIP": ("Tip Amount", "line_edit", r'^\d{1,2}%?$', 50),
            "DESSERT": ("Dessert", "combo", ["Tiramisu", "Apple Tart", "Cheesecake"], 200),
            "LABEL2": (" ", "label", None, 400), "HOME": ("Home", "combo", ["A", "B", "C"], 200),
            "SITES.@HOME": ("Home Location", "read_only", None, 180),
            "SITES.B": ("Location B", "read_only", None, 180),
            "SITES": ("Sites", "line_edit", None, 300), "items": ("Items", "line_edit", None, 300),
            "people": ("People", "line_edit", None, 300),
        },
    }

    formats = {
        "expert": {
            "NAMES": ("Layers", "line_edit", None, 680),
            "LAYER_LIST": ("Layer list", "line_edit", None, 680),
            "LAYER": ("Active Layer", "combo", ["A", 'B', 'C', "D", 'E', 'F', "G", 'H', 'I'], 204),
            "NAMES.@LAYER": ("Layer Name", "line_edit", r'^\w+$', 200),
            "FILES.@LAYER": ("Elevation File(s)", "text_edit", rgx_token_suffix(".tif"), 680),
            "SOURCES.@LAYER": ("Source", "line_edit", None, 680),
            "LICENSES.@LAYER": ("License", "line_edit", None, 680),
            "LABEL1": ("", "label", None, 400), "LABEL2": ("", "label", None, 400),
            "WARP1": ("CRS", "line_edit", rgx_starts("-t_srs"), 500),
            "WARP4": ("Performance", "line_edit", None, 500),
            "WARP2": ("gdalwarp", "line_edit", rgx_multiple_switches(), 500), "WARP3": (
                "Resampling", "combo",
                ["-r bilinear", '-r cubic', '-r cubicspline', '-r lanczos', " "], 505),
            "LABEL3": ("", "label", None, 400), "LABEL4": ("", "label", None, 400),
        }, "basic": {
            "NAMES.@LAYER": ("Layer", "read_only", None, 180),
            "FILES.@LAYER": ("Elevation File(s)", "text_edit", r"^[^/]*\.tif[^/]*$", 680),
            "LABEL3": ("", "label", None, 400), "LABEL4": ("", "label", None, 400),
        }
    }

    # Create a SettingsWidget and configure the display/edit fields based on 'formats'.
    # Data is linked between the widgets and the corresponding fields in the config file
    #settings_widget = SettingsWidget(config, formats, mode="expert", redisplay_keys=["LAYER"])


    # Create color settings widget to display and edit the color table settings
    settings_widget = SettingsWidget(config, formats,"expert",["LAYER"])

    # Link Save button to SettingsWidget.save to commit changes back to YAML file.
    save_button = QPushButton("Save")
    save_button.clicked.connect(settings_widget.save)

    # Set up the display with the settings widget and save button
    window = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(settings_widget)
    layout.addWidget(save_button)
    window.setLayout(layout)

    # Display the settings from the config file and allow editing
    settings_widget.display()

    window.show()
    sys.exit(app.exec())
