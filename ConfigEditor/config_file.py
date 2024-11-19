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
    Handles loading and saving YAML files.

    Extends DataManager:
        - Implements YAML specific file _load_data, _save_data

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
        # This will load data from YAML files
        data = yaml.safe_load(f)

        # Handle case where data is None (empty file) or incorrect format
        if data is None:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)  # Delete corrupted file if it exists
        return data

    def _save_data(self, f, data):
        """
        Save data in YAML format

        Args:
            f (file): The file object to write to.
            data (dict): The modified data to save

        Raises:
            ValueError: If _data is empty
        """
        if data:
            # Save the updated data to the file
            yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False)
            self.unsaved_changes = False
        else:
            raise ValueError("_data is None")


# Regex patterns
def rgx_token_suffix(token_suffix):
    """
    Returns a regex pattern where all tokens must end with token_suffix.

    Parameters:
        token_suffix (str): The required suffix for each token.
    """
    return rf"^(?:\S*{token_suffix}\s*)+$"


def rgx_multiple_switches():
    """
    Returns a regex pattern containing multiple switches,
    where each switch is optional and may include arguments.

    The pattern matches switches that may start with either one or two hyphens
    and may optionally have key-value pairs following the switch.
    """
    return r"^(?:--?\w+(?:\s+\w+(?:=[\w/%]+)?)?\s*)+$"


def rgx_starts(pattern):
    """
    Returns a regex pattern that starts with the specified pattern
    followed by a whitespace and then a non-whitespace token.

    Parameters:
        pattern (str): The initial pattern that the string must start with.
    """
    return rf"^{pattern}\s+\S+$"


def rgx_includes(pattern):
    """
    Returns a regex pattern that includes the specified pattern anywhere.

    Parameters:
        pattern (str): The pattern that must be included somewhere in the string.
    """
    return rf".*{pattern}.*"
