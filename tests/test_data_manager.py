import pytest
from unittest.mock import mock_open, patch

from ConfigEditor.data_manager import DataManager, AnyDataHandler, ListDataHandler


# Mock implementation of DataManager for testing purposes
class TestDataManager(DataManager):
    def _load_data(self, f):
        return {"key1": "val1"}

    def _save_data(self, f, data):
        f.write("mock data")  # Simulate data saving


@pytest.fixture
def dict_data_manager():
    dm = TestDataManager()
    dm._data = {"name": "example", "nested": {"key": "value"}}
    return dm

@pytest.fixture
def list_data_manager():
    dm = TestDataManager()
    dm._data = ["item1", "item2", "item3"]
    return dm


# Test proxy files

def test_add_single_proxy(dict_data_manager):
    """
    Test adding a single proxy with associated keys.
    """
    dict_data_manager.add_proxy("proxy_file_1", ["key1", "key2"])

    assert dict_data_manager._get_proxy(
        "key1"
        ) == "proxy_file_1", "Key1 should be associated with proxy_file_1"
    assert dict_data_manager._get_proxy(
        "key2"
        ) == "proxy_file_1", "Key2 should be associated with proxy_file_1"
    assert dict_data_manager._get_proxy("key3") is None, "Key3 should not have an associated proxy"


def test_add_multiple_proxies(dict_data_manager):
    """
    Test adding multiple proxies with distinct keys.
    """
    dict_data_manager.add_proxy("proxy_file_1", ["key1"])
    dict_data_manager.add_proxy("proxy_file_2", ["key2", "key3"])

    assert dict_data_manager._get_proxy(
        "key1"
        ) == "proxy_file_1", "Key1 should be associated with proxy_file_1"
    assert dict_data_manager._get_proxy(
        "key2"
        ) == "proxy_file_2", "Key2 should be associated with proxy_file_2"
    assert dict_data_manager._get_proxy(
        "key3"
        ) == "proxy_file_2", "Key3 should be associated with proxy_file_2"


def test_add_proxy_duplicate_key(dict_data_manager):
    """
    Test adding a proxy with keys already associated with another proxy.
    """
    dict_data_manager.add_proxy("proxy_file_1", ["key1", "key2"])

    with pytest.raises(
            ValueError,
            match="Key 'key1' is already associated with another proxy file: proxy_file_1"
            ):
        dict_data_manager.add_proxy("proxy_file_2", ["key1"])


def test_add_proxy_overwrite(dict_data_manager):
    """
    Test that overwriting the proxy mapping is not allowed and raises an error.
    """
    dict_data_manager.add_proxy("proxy_file_1", ["key1"])
    with pytest.raises(
            ValueError,
            match="Key 'key1' is already associated with another proxy file: proxy_file_1"
            ):
        dict_data_manager.add_proxy("proxy_file_2", ["key1"])


def test_get_proxy_no_mapping(dict_data_manager):
    """
    Test `_get_proxy` for keys that do not exist in the mapping.
    """
    assert dict_data_manager._get_proxy(
        "nonexistent_key"
        ) is None, "Nonexistent keys should return None"

# Test DictDataHandler

# Test length of _data for dictionary manager
def test_dict_data_manager_len(dict_data_manager):
    assert len(dict_data_manager._data) == 2, "Incorrect length for dictionary data"

def test_dict_data_handler_get_nested_key():
    handler = AnyDataHandler()
    data = {"outer": {"inner": "value"}}
    assert handler.get(data, "outer.inner") == "value"
    assert handler.get(data, "outer.nonexistent") is None

def test_dict_data_handler_set_nested_key():
    handler = AnyDataHandler()
    data = {}
    handler.set(data, "outer.inner", "value")
    assert data["outer"]["inner"] == "value"

def test_dict_data_handler_get_level():
    handler = AnyDataHandler()
    data = {"files": {"layer1": "data1", "layer2": "data2"}}
    items = handler.get(data, "files")
    assert dict(items) == {"layer1": "data1", "layer2": "data2"}

def test_dict_data_handler_indirect_key():
    handler = AnyDataHandler()
    data = {"files": {"A": "dataA"}, "current_layer": "A"}
    result = handler.get(data, "files.@current_layer")
    assert result == "dataA"

# Test ListDataHandler

# Test length of _data for list manager
def test_list_data_manager_len(list_data_manager):
    assert len(list_data_manager._data) == 3, "Incorrect length for list data"

def test_list_data_handler_get_item():
    handler = ListDataHandler()
    data = ["a", "b", "c"]
    assert handler.get(data, 1) == "b"
    assert handler.get(data, 5) is None

def test_list_data_handler_set_item():
    handler = ListDataHandler()
    data = ["a", "b", "c"]
    handler.set(data, 1, "new_value")
    assert data[1] == "new_value"

def test_data_manager_list_insert(list_data_manager):
    list_data_manager.insert(1, "new_item")
    assert list_data_manager._data[1] == "new_item"

def test_data_manager_list_delete(list_data_manager):
    list_data_manager.delete(1)
    assert list_data_manager._data == ["item1", "item3"]

def test_data_manager_get_open_mode(dict_data_manager):
    assert dict_data_manager.get_open_mode() == "r"
    assert dict_data_manager.get_open_mode(write=True) == "w"

# Test DataManager property and internal methods
def test_data_manager_handler_initialization(dict_data_manager, list_data_manager):
    assert isinstance(dict_data_manager.handler, AnyDataHandler)
    assert isinstance(list_data_manager.handler, ListDataHandler)


# Test snapshot handling
def test_data_manager_snapshot_limit():
    dm = TestDataManager()
    dm._data = {}

    for i in range(dm.max_snapshots + 4):  # Exceed max_snapshots
        # Set data and snapshot it
        dm._data["value"] = f"snapshot_{i}"
        dm.snapshot_push()

    # After limit is reached: first item should still be item 0, last item should be last item
    assert len(dm.snapshots) == dm.max_snapshots  # max_snapshots limit
    assert dm.snapshots[0] == {'value': 'snapshot_0'}
    assert dm.snapshots[dm.max_snapshots - 1] == {'value': f'snapshot_{dm.max_snapshots + 3}'}


def test_data_manager_undo_no_data():
    dm = TestDataManager()
    # No data to undo.  Should have no effect
    dm.snapshot_undo()
    assert dm._data is None


def test_data_manager_undo():
    dm = TestDataManager()

    # Initialize data and create snapshot
    dm.init_data({"key1": "val0"})

    # Validate setup
    assert dm._data["key1"] == "val0", "Incorrect init"

    # Create 2 more snapshots: val1, val2
    for i in range(2):
        # Set data and snapshot it
        dm._data["key1"] = f"val{i + 1}"
        dm.snapshot_push()

    # Validate dm._data["key1"]
    assert dm._data["key1"] == "val2", "Incorrect setup"

    # Undo _data to last snapshot and validate
    dm._data["key1"] = "hot garbage"
    dm.snapshot_undo()
    assert dm._data["key1"] == "val2", "Undo did not revert to  2nd snapshot "

    # Undo _data another snapshot and validate
    dm._data["key1"] = "hot garbage"
    dm.snapshot_undo()
    assert dm._data["key1"] == "val1", "Undo did not revert to  1st snapshot"

    # Undo _data another snapshot and validate
    dm._data["key1"] = "hot garbage"
    dm.snapshot_undo()
    assert dm._data["key1"] == "val0", "Undo did not revert to initial1 "

    # Undo beyond 3 times; ensure initial still restored
    dm._data["key1"] = "hot garbage"
    dm.snapshot_undo()
    assert dm._data["key1"] == "val0", "Undo did not revert to initial2 "
