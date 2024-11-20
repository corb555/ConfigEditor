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
import json
import os

from ConfigEditor.data_manager import DataManager


class JsonConfig(DataManager):
    """
    Handles loading and saving JSON files.

    Extends DataManager:
        - Implements JSON specific file _load_data, _save_data

    Inherits DataManager base file handling functionality:
        - load, save, get, set, and undo.

    **Methods**:
    """

    def _load_data(self, f):
        """
        Load data from a YAML file

        Args:
            f (file): The file object to read from.
        """
        # Load data from JSON file
        data = json.load(f)

        # Handle case where data is None (empty file) or incorrect format
        if data is None:
            if os.path.exists(self.file_path):
                # File is unreadable
                print(f"WARNING: {self.file_path} is not a valid file.")
        return data

    def _save_data(self, f, data):
        """
        Save data in JSON format

        Args:
            f (file): The file object to write to.
            data (dict): The modified data to save

        Raises:
            ValueError: If _data is empty
        """
        if data:
            # Save the data to the file
            json.dump(data, f, indent=4)
            self.unsaved_changes = False
        else:
            raise ValueError("_data is None")
