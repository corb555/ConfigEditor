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

from abc import ABC, abstractmethod
import copy
import os
from typing import Dict, List, Union


class DataManager(ABC):
    """
    Abstract base class for managing data loading, saving, and handling
    for different data types (dict or list). The `DataManager` class
    includes functionality for tracking unsaved changes, undoing changes
    with snapshots, and abstract methods for data-specific load/save
    operations to be implemented by subclasses.

    Attributes:
        _data (Union[Dict, List]): Data  (either a dictionary or a list).
        file_path (str): Path of the file being managed.
        directory (str): Directory of the file being managed.
        unsaved_changes (bool): Flag indicating if there are unsaved changes.
        snapshots (List): Stack of snapshots for supporting undo functionality.
        _handler (Union[DictDataHandler, ListDataHandler]): Handler to operate on `_data` based
        on whether it's a Dict or a List.
        max_snapshots (int): Maximum number of snapshots for undo functionality.
    """

    def __init__(self):
        """Initialize """
        self._data = None
        self.file_path = None
        self.directory = None
        self.unsaved_changes = False
        self.snapshots = []  # Stack to store snapshots of _data for undo
        self._handler = None  # the handler for our data type
        self.max_snapshots = 5  # Maximum number of snapshots to retain for undo

    @property
    def handler(self):
        """ Initialize the handler when it's accessed for the first time."""
        if self._handler is None:
            self._set_data_handler()
        return self._handler

    def _set_data_handler(self):
        """Set the appropriate data handler based on _data type."""
        if isinstance(self._data, dict):
            self._handler = DictDataHandler()
        else:
            self._handler = ListDataHandler()

    @abstractmethod
    def _load_data(self, f) -> Union[Dict, List]:
        """
        Load data from file into _data and return either a dictionary or a list.
        """
        raise NotImplementedError(
            f"Subclass must implement {self.__class__.__name__}._load_data()"
        )

    @abstractmethod
    def _save_data(self, f, data):
        """Save _data to file. Must be implemented by subclasses."""
        raise NotImplementedError(
            f"Subclass must implement {self.__class__.__name__}._save_data()"
        )

    def load(self, path):
        """
        Load data from the specified file.
        """
        self.file_path = path
        self.directory = os.path.dirname(path)

        try:
            with open(path, self.get_open_mode()) as f:
                self._data = self._load_data(f)
                self._set_data_handler()
            self.unsaved_changes = False
            self.snapshots = []  # Clear snapshots
            self._create_snapshot()  # Save the initial state
            return True
        except (FileNotFoundError, IOError, ValueError, Exception):
            raise

    def get_open_mode(self, write=False):
        return 'w' if write else 'r'

    def save(self):
        """
        Manages the process of saving data to the file if there are unsaved changes.
        """
        if self.file_path is None:
            raise ValueError("File path cannot be None")

        if self.unsaved_changes:
            self._create_snapshot()  # Save the current state before writing to the file
            try:
                with open(self.file_path, self.get_open_mode(write=True)) as f:
                    self._save_data(f, self._data)
                self.unsaved_changes = False
            except (FileNotFoundError, IOError, RuntimeError):
                raise

    def undo(self):
        """Restore the previous state of _data from the snapshot history."""
        name = os.path.basename(self.file_path)
        if not self.snapshots:
            print(f"No {name} snapshots")
            return

        # Restore the last snapshot
        self._data = self.snapshots.pop()
        self.unsaved_changes = True  # Mark the data as unsaved since it was changed

    def _create_snapshot(self):
        """Create a snapshot of the current _data for undo functionality."""
        if len(self.snapshots) >= self.max_snapshots:
            self.snapshots.pop(0)  # Remove the oldest snapshot if we've reached the limit

        # Create a deep copy of _data to store as a snapshot
        self.snapshots.append(copy.deepcopy(self._data))

    def __getitem__(self, key_or_index):
        """Retrieve data from the internal _data structure."""
        return self.handler.get(self._data, key_or_index)

    def __setitem__(self, key, value):
        """Update data in the internal _data structure."""
        self.handler.set(self._data, key, value)
        self.unsaved_changes = True

    def __len__(self):
        if self._data:
            return len(self._data)
        else:
            return 0

    def insert(self, key, value):
        """Insert data into the internal _data structure."""
        self.handler.insert(self._data, key, value)
        self.unsaved_changes = True

    def delete(self, key):
        """Delete data from the internal _data structure."""
        self.handler.delete(self._data, key)
        self.unsaved_changes = True

    def set(self, key, value):
        """Wrapper to update data using __setitem__."""
        self.unsaved_changes = True
        self.__setitem__(key, value)

    def get(self, key_or_index, default=None):
        """Retrieve data from _data with a default if not found."""
        value = self.__getitem__(key_or_index)
        return value if value is not None else default

    def items(self):
        """Return items from _data if it's a dictionary, or the list itself if it's a list."""
        return self.handler.items(self._data)


class DataHandler(ABC):
    """
    Abstract base class with methods to get, set, and iterate over items within the data structure.
    """

    @abstractmethod
    def get(self, data, key):
        """
        Retrieve an item from the given data structure based on the provided key.

        Args:
            data (dict or list): The data structure to retrieve the item from.
            key (str or int): The key or index to access the item.

        Returns:
            The value corresponding to the key or index.
        """
        pass

    @abstractmethod
    def set(self, data, key, value):
        """
        Set an item in the data structure at the specified key or index.

        Args:
            data (dict or list): The data structure to modify.
            key (str or int): The key or index where the value should be set.
            value: The value to store at the specified location.
        """
        pass

    @abstractmethod
    def items(self, data):
        """
        Return an iterator over the items in the data structure.

        Args:
            data (dict or list): The data structure to iterate over.

        Returns:
            An iterator over the (key, value) pairs for dictionaries or (index, value) pairs for
            lists.
        """
        pass


class DictDataHandler(DataHandler):
    """
    Implementation of the DataHandler for handling dictionary data structures.
    Supports both regular and nested dictionary access, as well as indirect key references.
    """

    def get(self, data, key):
        """
        Retrieve a value from a dictionary, supporting both nested keys, indirect key references,
        and wildcards ('*') for returning all values under a given name.

        Args:
            data (dict): The dictionary to retrieve the value from.
            key (str): The key to access the value. Supports '.' for nested keys, '@' for
            indirect keys, and '*' for wildcards.

        Returns:
            The value associated with the key, or None if the key is not found.
        """
        # Handle indirect key references (e.g., FILES@LAYER)
        if "@" in key:
            main_key, indirect_ref = key.split("@", 1)
            ref = data.get(indirect_ref)
            if ref is not None:
                key = f"{main_key}{ref}"

        # Handle wildcard keys (e.g., name.*)
        if ".*" in key:
            main_key = key.split(".*")[0]
            return data.get(main_key, {}).items()

        # Handle nested keys
        keys = key.split('.')
        value = data
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return None

    def set(self, data, key, value):
        """
        Set a value in a dictionary, supporting nested key paths and indirect key references.

        Args:
            data (dict): The dictionary to modify.
            key (str): The key to set the value at. Supports '.' for nested keys and '@' for
            indirect keys.
            value: The value to store in the dictionary.
        """
        # Ignore set for wildcard keys (e.g., name.*)
        if ".*" in key:
            return

        # Handle indirect key case, e.g., FILES@LAYER
        if "@" in key:
            main_key, indirect_ref = key.split("@", 1)
            ref = data.get(indirect_ref)  # Resolve the indirect reference from data
            if ref is not None:
                key = key.replace(
                    f"@{indirect_ref}", ref
                )  # Replace '@LAYER' with the value of 'LAYER'

        keys = key.split('.')
        target = data

        # Traverse the dictionary to the correct level, except for the last key part
        for k in keys[:-1]:
            target = target.setdefault(k, {})  # Ensure intermediate dictionaries are created

        # Set the value for the final key part
        final_key = keys[-1]
        target[final_key] = value

    def items(self, data):
        """
        Return an iterator over the key-value pairs in the dictionary.

        Args:
            data (dict): The dictionary to iterate over.

        Returns:
            Iterator of (key, value) pairs.
        """
        return data.items()


def insert(data, idx, value):
    """Inserts a value into the list and tracks changes."""
    data.insert(idx, value)


def delete(data, idx):
    """Deletes an item from the list and tracks changes."""
    data.pop(idx)


class ListDataHandler(DataHandler):
    """
    Implementation of the DataHandler for handling list-like data structures.
    Provides basic get, set, and iteration functionality.
    """

    def get(self, data, index):
        """
        Retrieve an item from a list by index.

        Args:
            data (list): The list to retrieve the item from.
            index (int): The index of the item to retrieve.

        Returns:
            The value at the specified index, or None if the index is out of bounds.
        """
        if data:
            return data[index] if index < len(data) else None
        else:
            return None

    def set(self, data, index, value):
        """
        Set an item in a list at the specified index.

        Args:
            data (list): The list to modify.
            index (int): The index at which to set the value.
            value: The value to store at the specified index.

        Raises:
            IndexError: If the index is out of range of the list.
            ValueError: If data is empty
        """
        if data:
            if index < len(data):
                data[index] = value
                # todo self.unsaved_changes = True
            else:
                raise IndexError(f"List index out of range: {index}")
        else:
            raise ValueError(f"Cannot set value on empty data")

    def items(self, data):
        """
        Return an iterator over the index-value pairs in the list.

        Args:
            data (list): The list to iterate over.

        Returns:
            Iterator of (index, value) pairs.
        """
        return enumerate(data)


def _validate_file_exists(path):
    """Check if a file exists at the given path, raising an error if not."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
