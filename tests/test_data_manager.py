import pytest

from ConfigEditor.data_manager import DataManager, DictDataHandler, ListDataHandler


# Mock implementation of DataManager for testing purposes
class TestDataManager(DataManager):
    def _load_data(self, f):
        return {"sample_key": "sample_value"}

    def _save_data(self, f, data):
        pass

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

# Test DictDataHandler
def test_dict_data_handler_get_nested_key():
    handler = DictDataHandler()
    data = {"outer": {"inner": "value"}}
    assert handler.get(data, "outer.inner") == "value"
    assert handler.get(data, "outer.nonexistent") is None

def test_dict_data_handler_set_nested_key():
    handler = DictDataHandler()
    data = {}
    handler.set(data, "outer.inner", "value")
    assert data["outer"]["inner"] == "value"


def test_dict_data_handler_get_level():
    handler = DictDataHandler()
    data = {"files": {"layer1": "data1", "layer2": "data2"}}
    items = handler.get(data, "files")
    assert dict(items) == {"layer1": "data1", "layer2": "data2"}

def test_dict_data_handler_indirect_key():
    handler = DictDataHandler()
    data = {"files": {"A": "dataA"}, "current_layer": "A"}
    result = handler.get(data, "files.@current_layer")
    assert result == "dataA"

# Test ListDataHandler
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

# Test DataManager methods for list-based data
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
    assert isinstance(dict_data_manager.handler, DictDataHandler)
    assert isinstance(list_data_manager.handler, ListDataHandler)

def test_data_manager_snapshot_limit():

    dm = TestDataManager()
    dm._data = {}

    for i in range(dm.max_snapshots + 4):  # Exceed max_snapshots
        # Set data and snapshot it
        dm._data["value"] = f"snapshot_{i}"
        dm.create_snapshot()

    # After limit is reached: first item should still be item 0, last item should be last item
    assert len(dm.snapshots) == dm.max_snapshots  # max_snapshots limit
    assert dm.snapshots[0] == {'value': 'snapshot_0'}
    assert dm.snapshots[dm.max_snapshots - 1] == {'value': f'snapshot_{dm.max_snapshots + 3}'}
