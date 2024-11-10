#  Copyright (c) 2024. Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated
#  documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
#  persons to whom the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
#  Software.
#
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#  WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import pytest

from ColorReliefEditor.data_manager import ListDataHandler


class TestListDataHandler:
    def setup_method(self):
        """Set up a new ListDataHandler instance before each test."""
        self.handler = ListDataHandler()

    def test_get_valid_index(self):
        """Test retrieving a value at a valid index."""
        data = ['a', 'b', 'c']
        key = 1
        result = self.handler.get(data, key)
        assert result == 'b', f"Expected 'b', but got {result}"

    def test_get_invalid_index(self):
        """Test retrieving a value at an invalid index."""
        data = ['a', 'b', 'c']
        key = 5
        result = self.handler.get(data, key)
        assert result is None, "Expected None for an invalid index"

    def test_set_valid_index(self):
        """Test setting a value at a valid index."""
        data = ['a', 'b', 'c']
        key = 1
        self.handler.set(data, key, 'z')
        assert data[1] == 'z', "Value at index 1 should be 'z'"

    def test_set_invalid_index(self):
        """Test setting a value at an invalid index (should raise IndexError)."""
        data = ['a', 'b', 'c']
        key = 5
        with pytest.raises(IndexError):
            self.handler.set(data, key, 'z')

    def test_items(self):
        """Test iterating over the items in the list."""
        data = ['a', 'b', 'c']
        expected_items = [(0, 'a'), (1, 'b'), (2, 'c')]
        items = list(self.handler.items(data))
        assert items == expected_items, f"Expected items {expected_items}, but got {items}"

    def test_set_extend_list(self):
        """Test setting a value at an index greater than the current list length """
        data = ['a', 'b']
        key = 3
        with pytest.raises(IndexError):
            self.handler.set(data, key, 'd')
