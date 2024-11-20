import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout

from ConfigEditor.yaml_config import YamlConfig
from ConfigEditor.settings_widget import SettingsWidget

"""
A sample application that loads  data from a config file, initializes
the SettingsWidget for displaying and editing settings, and provides a save button
and an undo button.
"""

def create_window(settings):
    # Create Save button
    save_button = QPushButton("Save")
    save_button.clicked.connect(settings_widget.save)

    # Create Undo button
    undo_button = QPushButton("Undo")
    undo_button.clicked.connect(settings_widget.undo)

    # Create button bar
    button_bar = QHBoxLayout()
    button_bar.addWidget(save_button)
    button_bar.addWidget(undo_button)

    # Set up the display with the settings widget and buttons
    window = QWidget()
    layout = QVBoxLayout()

    layout.addWidget(settings)
    layout.addLayout(button_bar)

    window.setLayout(layout)
    return window


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load YAML file
    config = YamlConfig()
    success = config.load("tests/sample.yml")

    if not success:
        sys.exit()

    # Create the UI layout for the fields in the YML file.
    formats = {
        "layout1": {
            "LABEL1": ("Menu", "label", None, 400),
            "TIP": ("Tip Amount", "line_edit", r'^\d{1,2}%?$', 50),
            "DESSERT": ("Dessert", "combo", ["Tiramisu", "Apple Tart", "Cheesecake"], 200),
            "HOME": ("Home", "combo", ["A", "B", "C"], 200),
            "SITES.@HOME": ("Home Location", "read_only", None, 180),
            "SITES.B": ("Location B", "line_edit", None, 180),
            "SITES": ("Sites", "line_edit", None, 300),
        },
    }

    # Create the settings widget to display and edit the YAML settings
    settings_widget = SettingsWidget(config, formats, "layout1", ["HOME"])

    # Create main window and add settings_widget and buttons
    window = create_window(settings_widget)

    # Display the settings
    settings_widget.display()

    window.show()
    sys.exit(app.exec())
