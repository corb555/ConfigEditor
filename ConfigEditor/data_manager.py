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
from typing import Dict, List, Union, Any


class DataManager(ABC):
    """
       Abstract base class for managing data, providing functions for: load, save, get, set, and
       undo.

       Subclasses must implement file-specific data handling methods: `_load_data` and `_save_data`.

       Attributes:
           _data (Union[Dict, List]): The main data structure being managed (dictionary or list).
           file_path (str): Path to the file associated with the data.
           directory (str): Directory containing the file.
           unsaved_changes (bool): Indicates if there are unsaved changes in the data.
           snapshots (List): Stack of snapshots for supporting undo functionality.
           max_snapshots (int): Maximum number of snapshots retained for undo operations.
           proxy_mapping (Dict): Maps keys to proxy files for granular build system dependencies.

        **Methods**:
       """

    def __init__(self):
        """Initialize """
        self._data = None
        self.file_path = None
        self.directory = None
        self.unsaved_changes = False
        self.snapshots = []  # Stack to store snapshots of _data for undo
        self._handler = None  # the handler for our data type
        self.max_snapshots = 6  # Maximum number of snapshots to retain for undo
        self.proxy_mapping = {}  # Dictionary to map keys to proxy files

    @abstractmethod
    def _load_data(self, f) -> Union[Dict, List]:
        """
         Load data from a file and return as a dictionary or list.
         Subclasses must implement this method to define file-specific behavior.

         Args:
             f: File object to load data from.

         Returns:
             Union[Dict, List]: The loaded data.

         Raises:
            ValueError: If the file is empty or cannot be parsed.
         """
        raise NotImplementedError(
            f"Subclass must implement {self.__class__.__name__}._load_data()"
        )

    @abstractmethod
    def _save_data(self, f, data):
        """
        Save data to a file.
        Subclasses must implement this method to define file-specific behavior.

        Args:
            f: File object to save data to.
            data: Data to be saved.
        Raises:
            RuntimeError: If the file cannot be saved.
        """
        raise NotImplementedError(
            f"Subclass must implement {self.__class__.__name__}._save_data()"
        )

    def load(self, path):
        """
        Load data from the specified file and initialize  state.
        Create an initial snapshot for undo functionality.

        Args:
            path (str): Path to the file to load.

        Returns:
            bool: True if the file was loaded successfully.

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If there is an issue reading the file.
            ValueError: If the file contents are invalid.
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
            self.create_snapshot()  # Save the initial state
            return True
        except (FileNotFoundError, IOError, ValueError, Exception):
            raise

    def get_open_mode(self, write=False):
        """
        Provides the file mode for the data file.
        Default is 'w' for write mode, 'r' for read mode.
        Override for binary or other modes.

        Args:
            write (bool): Whether the file is being opened for writing.

        Returns:
            str: 'w' for write mode, 'r' for read mode.
        """
        return 'w' if write else 'r'

    def save(self):
        """
        Save the current data to the file if it has been modified.
        Create a snapshot of the data for undo feature.

        Raises:
            ValueError: If the file path or data is None.
            IOError: If there is an issue saving the file.
        """
        if self.file_path is None:
            raise ValueError("File path cannot be None")

        if self._data is None:
            raise ValueError("Data cannot be None")

        if self.unsaved_changes:
            self.create_snapshot()  # Save the current state to snapshot stack
            try:
                with open(self.file_path, self.get_open_mode(write=True)) as f:
                    self._save_data(f, self._data)
                self.unsaved_changes = False
            except (FileNotFoundError, IOError, RuntimeError):
                raise

    def set(self, key, value):
        """
        Update the data with a new value and check for proxy updates.

        Args:
            key: Key for the data.
            value: New value to set.
        """
        self.unsaved_changes = True
        self.__setitem__(key, value)

        # Check if updating this key should trigger a touch to a proxy_file
        proxy_file = self._get_proxy(key)
        if proxy_file is not None:
            touch_file(proxy_file)

    def get(self, key_or_index, default=None):
        """
        Retrieve a value from the data, returning a default if not found.

        Args:
            key_or_index: Key or index for the data.
            default: Default value to return if the key or index is not found.

        Returns:
            The value associated with the key or index, or the default.
        """
        value = self.__getitem__(key_or_index)
        return value if value is not None else default

    def __getitem__(self, key_or_index):
        """
        Retrieve a value from the data using the specified key or index.

        Args:
            key_or_index: Key or index for the data.

        Returns:
            The value associated with the specified key or index.
        """
        return self.handler.get(self._data, key_or_index)

    def __setitem__(self, key, value):
        """
        Update the data with a new value at the specified key or index.

        Args:
            key: Key or index for the data.
            value: New value to set.
        """
        self.handler.set(self._data, key, value)
        self.unsaved_changes = True

    def insert(self, key, value):
        """
        Insert a new item into the data.

        Args:
            key: Key or index for the new item.
            value: Value to insert.
        """
        self.handler.insert(self._data, key, value)
        self.unsaved_changes = True

    def delete(self, key):
        """
        Remove an item from the data.

        Args:
            key: Key or index of the item to remove.
        """
        self.handler.delete(self._data, key)
        self.unsaved_changes = True

    def undo(self):
        """
        Restore the data to the previous state using the snapshot stack.

        The first snapshot remains in the stack to always allow undo to initial state.
        """
        if not self.snapshots:
            return

        # Pop last snapshot unless it is the only one left
        self._data = self.snapshots.pop() if len(self.snapshots) != 1 else self.snapshots[0]
        self.unsaved_changes = True

    def create_snapshot(self):
        """
        Save the current state of the data as a snapshot for undo functionality.

        If the maximum number of snapshots is reached, the second oldest snapshot is removed.
        """
        if len(self.snapshots) >= self.max_snapshots:
            # Remove the second-oldest snapshot
            self.snapshots.pop(1)

        # Create a deep copy of _data to store as a snapshot
        self.snapshots.append(copy.deepcopy(self._data))

    def __len__(self):
        """
        Get the number of items in the data.

        Returns:
            int: Number of items in the data.
        """
        if self._data:
            return len(self._data)
        else:
            return 0

    def items(self):
        """
        Get an iterator over the items in the data.

        Returns:
            Iterator: An iterator over the data items.
        """
        return self.handler.items(self._data)

    def init_data(self, data: Dict[str, Any]):
        """
        Initialize the data and set the appropriate data handler.

        Args:
            data (Dict[str, Any]): New data to initialize.
        """
        self._data = data
        self._set_data_handler()
        self.unsaved_changes = True

    def create(self, data: Dict[str, Any]):
        """
        Create a new config file with the specified data.

        Args:
            data (Dict[str, Any]): Data to save in the new file.
        """
        self.init_data(data)
        self.save()

    def add_proxy(self, proxy_file, proxy_update_keys):
        """
        Add a proxy file and its associated update keys.
        If any of these keys are updated, they will trigger a touch to this proxy_file.
        This can be used to improve the granularity of dependencies for build management systems.
        The build system can set a dependency on the proxy_file which is only updated for a subset
        of fields in the config file rather than rebuilding from any change to the config file.

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

    def _get_proxy(self, key):
        """
        Retrieve the proxy file associated with a given key, if set.

        Args:
            key (str): The key to look up.

        Returns:
            str or None: The proxy file associated with the key, or None if not found.
        """
        return self.proxy_mapping.get(key)

    @property
    def handler(self):
        """
        Initialize the data handler when it's accessed for the first time.
        There is a separate data handler for Dict data and List data
        """
        if self._handler is None:
            self._set_data_handler()
        return self._handler

    def _set_data_handler(self):
        """Set the appropriate data handler based on _data type."""
        if isinstance(self._data, dict):
            self._handler = DictDataHandler()
        else:
            self._handler = ListDataHandler()


def touch_file(filename):
    """
    Set the file's modification and access time to the current time.

    Args:
        filename (str): Path to the file.
    """
    with open(filename, 'a'):
        os.utime(filename, None)


class DataHandler(ABC):
    # Abstract base class with methods to get, set, and iterate over items within the data
    # structure.
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
    """Inserts a value into the list"""
    data.insert(idx, value)


def delete(data, idx):
    """Deletes an item from the list"""
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
