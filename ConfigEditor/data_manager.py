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
    Abstract base class for managing data loading, saving, and updating.
    The `DataManager` class
    includes functionality for tracking unsaved changes, undoing changes,
    and abstract methods for data-specific load/save
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
        self.proxy_mapping = {}  # Dictionary to map keys to proxy files

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

    def init_data(self, data):
        """
        Overwrite _data with data provided.  Set data_handler.
        Args:
            data:

        Returns:

        """
        self._data = data
        self._set_data_handler()
        self.unsaved_changes = True

    def create(self, data):
        """
        Create and save a new configuration file with the data provided

        Args:
            data (dict): The initial data to create
        """
        self.init_data(data)
        self.save()

    def load(self, path):
        """
        Load data from the specified file.
        """
        # Clear any proxy keys
        self.proxy_mapping = {}  # Dictionary to map keys to proxy files

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

    def add_proxy(self, proxy_file, proxy_update_keys):
        """
        Add a proxy file and its associated update keys.
        If any of these keys are updated, they will trigger a touch to this proxy_file.
        This can be used to improve the granularity of dependencies for build management systems.
        The build system can set a dependency on the proxy_file which is only updated for a subset
        of fields in the config file.

        Args:
            proxy_file (str): The file to touch when any associated key is updated.
            proxy_update_keys (List[str]): List of keys that trigger a touch to this proxy_file.
        """
        for key in proxy_update_keys:
            if key in self.proxy_mapping:
                raise ValueError(
                    f"Key '{key}' is already associated with another proxy file: "
                    f"{self.proxy_mapping[key]}"
                )
            self.proxy_mapping[key] = proxy_file

    def get_proxy(self, key):
        """
        Retrieve the proxy file associated with a given key, if it exists.

        Args:
            key (str): The key to look up.

        Returns:
            str or None: The proxy file associated with the key, or None if not found.
        """
        return self.proxy_mapping.get(key)

    def get_open_mode(self, write=False):
        return 'w' if write else 'r'

    def save(self):
        """
        Manages the process of saving data to the file if there are unsaved changes.
        """
        if self.file_path is None:
            raise ValueError("File path cannot be None")

        if self._data is None:
            raise ValueError("Data cannot be None")

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

        # Check if updating this key should trigger a touch to a proxy_file
        proxy_file = self.get_proxy(key)
        if proxy_file is not None:
            touch_file(proxy_file)

    def get(self, key_or_index, default=None):
        """Retrieve data from _data with a default if not found."""
        value = self.__getitem__(key_or_index)
        return value if value is not None else default

    def items(self):
        """Return items from _data if it's a dictionary, or the list itself if it's a list."""
        return self.handler.items(self._data)


def touch_file(filename):
    """
    Set the file's modification and access time to the current time.

    Args:
        filename (str): Path to the file.
    """
    with open(filename, 'a'):
        print(f"touch_file {filename}")
        os.utime(filename, None)


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
        Retrieve a value from a dictionary, supporting both nested keys, and indirect key
        references.

        Args:
            data (dict): The dictionary to retrieve the value from.
            key (str): The key to access the value. Supports '.' for nested keys, '@' for
            indirect keys.

        Returns:
            The value associated with the key, or None if the key is not found.
        """
        # Handle indirect key references (e.g., FILES@LAYER)
        if "@" in key:
            main_key, indirect_ref = key.split("@", 1)
            ref = data.get(indirect_ref)
            if ref is not None:
                key = f"{main_key}{ref}"

        # Handle nested dictionaries, with each sub-key separated by "."
        keys = key.split('.')
        value = data
        try:
            for k in keys:
                if not isinstance(value, dict):
                    # Ensure we are dereferencing a dictionary
                    print(f"Not a dict. Type: {type(value)} key={k}")
                    return value
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
            if k in target and not isinstance(target[k], dict):
                raise TypeError(
                    f"Cannot set value for {key}: Intermediate key '{k}' is not a dictionary."
                )

            # Ensure intermediate dictionaries are created
            target = target.setdefault(k, {})

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

    def set(self, data, index, item):
        """
        Set an item in a list at the specified index.

        Args:
            data (list): The list to modify.
            index (int): The index at which to set the value.
            item: The item to store at the specified index.

        Raises:
            IndexError: If the index is out of range of the list.
            ValueError: If data is empty
        """
        if data:
            if index < len(data):
                data[index] = item  # todo self.unsaved_changes = True
            else:
                raise IndexError(f"List index out of range: {index}")
        else:
            raise ValueError(f"Cannot set value on empty data")

    def insert(self, data_list, idx, item):
        """
        Insert an item in a list at the specified index.

        Args:
            data_list (list): The list to modify.
            idx (int): The index at which to insert the value.
            item: The value to store at the specified index.

        Raises:
            IndexError: If the index is out of range for insertion.
            ValueError: If data_list is empty.
        """
        # Validate that data_list is non-empty
        if not data_list:
            raise ValueError("Cannot insert into an empty list")

        # Ensure idx is within the acceptable range for insertion
        if idx < 0 or idx > len(data_list):
            raise IndexError(
                f"Index {idx} is out of range for insertion in a list of length {len(data_list)}"
            )

        # Insert the item at the specified index
        data_list.insert(idx, item)

    def delete(self, data_list, idx):
        """
        Delete the item in the list at the specified index.

        Args:
            data_list (list): The list to modify.
            idx (int): The index of the item to delete.

        Raises:
            IndexError: If the index is out of range for deletion.
            ValueError: If data_list is empty.
        """
        # Check if data_list is empty
        if not data_list:
            raise ValueError("Cannot delete from an empty list")

        # Ensure idx is within the allowable range for deletion
        if idx < 0 or idx >= len(data_list):
            raise IndexError(
                f"Index {idx} is out of range for deletion in a list of length {len(data_list)}"
            )

        # Delete the item at the specified index
        del data_list[idx]

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
