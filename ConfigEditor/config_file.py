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
import os

import yaml

from ConfigEditor.data_manager import DataManager


class ConfigFile(DataManager):
    """
    Handles loading, updating, and saving data in a YML file.

    Subclass of `DataManager`:
        - Inherits base file handling functionality: file loading, saving, and change
        tracking.
        - Implements methods specific to the YML file format, including custom
        parsing and saving logic.
    """

    def _load_data(self, f):
        """
        Load data from a YAML file

        Args:
            f (file): The file object to read from.

        Raises:
            ValueError: If the file is empty.
            RuntimeError: If the file cannot be parsed.
        """
        try:
            # This will load data from YML files
            data = yaml.safe_load(f)

            # Handle case where data is None (empty file) or incorrect format
            if data is None:
                if os.path.exists(self.file_path):
                    os.remove(self.file_path)  # Delete corrupted file if it exists
                raise ValueError(
                    f"YAML file {self.file_path} is empty or could not be parsed correctly."
                )
            return data
        except Exception as e:
            raise RuntimeError(f"Error while loading data: {e}") from e

    def _save_data(self, f, data):
        """
        Save data in YML format

        Args:
            f (file): The file object to write to.
            data (dict): The modified data to save

        Raises:
            ValueError: If _data is None.
            RuntimeError: If the file cannot be written.
        """
        try:
            if data:
                # Save the updated data to the file
                yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)
                self.unsaved_changes = False
            else:
                raise ValueError("_data is None")
        except Exception as e:
            raise RuntimeError(f"Error while saving data: {e}") from e

    def create(self, data):
        """
        Create and save a new configuration with the data provided

        Args:
            data (dict): The initial data to create
        """
        self._data = data
        self._set_data_handler()
        self.unsaved_changes = True
        self.save()

    def save(self):
        """
        Save the current configuration to the file.

        Raises:
            RuntimeError: If there is an issue saving the configuration.
        """
        if self.unsaved_changes:
            try:
                with open(self.file_path, 'w') as f:
                    self._save_data(f, self._data)
            except Exception as e:
                raise RuntimeError(f"Error while saving configuration: {e}") from e
            self.unsaved_changes = False
