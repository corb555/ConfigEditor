import pytest

from structured_text import (data_category, get_regex, parse_dict, parse_list, to_text,
                             validate_format, DICT_PATTERN, LIST_PATTERN, DataCategory)


# Test for determine_type
@pytest.mark.parametrize(
    "value, expected_type",
    [(10, DataCategory.SCALAR), (9.3, DataCategory.SCALAR), ("string", DataCategory.SCALAR),
        (True, DataCategory.SCALAR), ([1, 2, 3], DataCategory.LIST),
        (["a", "b"], DataCategory.LIST), ([1, "a", 2.5], DataCategory.LIST),
        ({"key": "value"}, DataCategory.DICT), ({"key": 1, "another_key": True}, DataCategory.DICT),
        ([[1, 2], [3, 4]], DataCategory.COMPLEX), ({"key": [1, 2, 3]}, DataCategory.COMPLEX),
        (None, DataCategory.SCALAR)],
    ids=["scalar_int", "scalar_float", "scalar_str", "scalar_bool", "list_int", "list_str",
         "list_mixed", "dict_simple", "dict_mixed", "dict_with_list", "nested_list", "None"]
)
def test_determine_type(value, expected_type):
    assert data_category(value) == expected_type


# Test for get_regex
@pytest.mark.parametrize(
    "value, expected_regex",
    [({"key": "value"}, DICT_PATTERN), (["item1", "item2"], LIST_PATTERN), (10, None),
     ("text", None), ([[1, 2], [3, 4]], None), ({"key": [1, 2, 3]}, None)],
    ids=["dict_regex", "list_regex", "scalar_int_regex", "scalar_str_regex", "nested_list_regex",
         "dict_with_list_regex"]
)
def test_get_regex(value, expected_regex):
    assert get_regex(value) == expected_regex


# Test for parse_dict
@pytest.mark.parametrize(
    "text, expected_result, should_raise",
    [("valid_format: value1, key2: value2", {"valid_format": "value1", "key2": "value2"}, False),

     ("  valid_with_spaces  :   value1  , key2:  value2 ", {"valid_with_spaces": "value1", "key2": "value2"}, False),
     ("", {}, False), (None, {}, False),

     ("valid_url_in_value: http://example.com, key2: value2",
                                          {"valid_url_in_value": "http://example.com", "key2": "value2"}, False),

     ("key_with_json: {'nested_key': 'nested_value'}, simple_key: simple_value",
      {"key_with_json": "{'nested_key': 'nested_value'}", "simple_key": "simple_value"}, False),

     # Negative cases
     ("missing_value: value1, key2", {}, True), ("missing_value = value1, key2: value2", {}, True),

     ("invalid_separator: value1, extra text", {}, True), ("invalid_separator", {}, True),

     ("unmatched_braces: {nested_key: nested_value", {'unmatched_braces': '{nested_key: nested_value'}, False),
     ("missing_closing_brace: {nested_key: value1, nested_key2", {}, True),

     ("pseudo_nested: {inner_key1: inner_value1, inner_key2: inner_value2}, outer_key2: value2",
             {'pseudo_nested': '{inner_key1: inner_value1', 'inner_key2': 'inner_value2}', 'outer_key2': 'value2'}, False),
     ("invalid_nested_format: {nested_key: nested_value}", {'invalid_nested_format': '{nested_key: nested_value}'}, False)],
    ids=["valid_format", "valid_format_with_spaces", "empty_string", "none_input",
         "valid_url_in_value", "valid_json_in_value", "missing_value", "invalid_separator",
         "extra_text", "no_key_value", "unmatched_braces", "missing_closing_brace", "pseudo_nested",
         "invalid_nested_format"]
)
def test_parse_dict(text, expected_result, should_raise):
    if should_raise:
        with pytest.raises(ValueError):
            parse_dict(text)
    else:
        assert parse_dict(text) == expected_result


# Test for parse_list
@pytest.mark.parametrize(
    "text, expected_result, should_raise", [("'item1', 'item2'", ["item1", "item2"], False), (
            "'item1', 'item2', 'item3'", ["item1", "item2", "item3"], False),
                                            ("   'item1' , 'item2'   ", ["item1", "item2"], False),
                                            ("", [], False),

                                            # Negative cases
                                            ("item1, item2", [], True),
                                            ("'item1', item2", [], True),
                                            ("'item1', 'item2' extra text", [], True)],
    ids=["valid_list", "valid_list_with_three_items", "list_with_spaces", "empty_list",
         "missing_quotes", "missing_quotes_second_item", "extra_text_outside_list"]
)
def test_parse_list(text, expected_result, should_raise):
    if should_raise:
        with pytest.raises(ValueError):
            parse_list(text)
    else:
        assert parse_list(text) == expected_result


# Test for format_as_text
@pytest.mark.parametrize(
    "value, expected_result", [({"key1": "value1", "key2": "value2"}, "key1: value1, key2: value2"),
                               (["item1", "item2"], "'item1', 'item2'"), ("text", "text"),
                               (123, "123")],
    ids=["dict_format", "list_format", "scalar_str_format", "scalar_int_format"]
)
def test_format_as_text(value, expected_result):
    assert to_text(value) == expected_result


# Test for validate_format
@pytest.mark.parametrize(
    "text, pattern, expected_result",
    [("'item1', 'item2'", LIST_PATTERN, True), ("key1=value1, key2:value2", DICT_PATTERN, False),
        ("[item1, item2]", LIST_PATTERN, False)],
    ids=["valid_list_format", "invalid_dict_format", "invalid_list_format"]
)
def test_validate_format(text, pattern, expected_result):
    assert validate_format(text, pattern) == expected_result
