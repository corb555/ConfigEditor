from enum import Enum
import re

"""
This module converts simple data structures to text for editing and then converts from text
back to a data structure.

Functions: 

to_text - Converts a dict, list, scalar,etc into a string representation for display or editing.
parse_text - Parses a string into the requested data structure (scalar, dictionary, list, etc.).
data_category - Identifies the data category of a value (SCALAR, COMPLEX, LIST, DICT, etc.).
validate_format - Validates if a string fully matches a specified regex pattern.

"""


class DataCategory(Enum):
    """
    Enum for representing different data types.
    """
    SCALAR = "scalar"
    LIST = "list"
    DICT = "dict"
    COMPLEX = "complex"


# Regular expression patterns for parsing dict and list text formats

# Regex for dict: "key: value, key: value" format
DICT_PATTERN = r"\s*([^\s:,][^:,]*?)\s*:\s*([^,]+?)\s*(?:,|$)"

# Regex for list: 'item1','item2' format
LIST_PATTERN = r"\s*\s*(['\"])([^'\"]*?)\1(?:\s*,\s*\1([^'\"]*?)\1)*\s*\s*"


def to_text(item):
    """
    Converts a dict, list, scalar, etc. into a string representation for display or editing.

    Parameters:
        item: The data structure to format (dict, list, or scalar).

    Returns:
        str: A formatted string representation of the item.

    Output Format:
        - For a dictionary:
          Each key-value pair is formatted as `key: value` and pairs are separated by commas.
          Example: {"key1": "value1", "key2": 42} -> "key1: value1, key2: 42"

        - For a list:
          Each element is enclosed in single quotes and separated by commas.
          Example: ["item1", "item2", 3] -> "'item1', 'item2', '3'"

        - For a scalar:
          The scalar value is converted to a string.
          Example: 42 -> "42"
    """

    if isinstance(item, dict):
        # Format each key-value pair as "key: value", separated by commas
        return ", ".join(f"{key}: {val}" for key, val in item.items())
    elif isinstance(item, list):
        # Enclose each element in single quotes, separated by commas
        return ", ".join(f"'{str(element)}'" for element in item)
    else:
        # Convert scalar directly to string
        return str(item)


def parse_text(text, category, rgx):
    """
    Parses text into the requested data structure (dictionary, list, or scalar). Scalar
    returns a string and is validated against the supplied regex pattern. Complex data
    structures are not supported.

    Parameters:
        text (str): The string to parse.
        category (DataCategory): The target data category (SCALAR, LIST, DICT).
        rgx (str): A regular expression to validate the input text format for scalars.

    Returns:
        tuple: (data, is_valid), where data is the resulting data structure
               and is_valid is a boolean indicating the validity of the format.
    """
    if category in {DataCategory.DICT, DataCategory.LIST}:
        if rgx:
            print("parse_text: rgx only supported for SCALAR data category.")
        try:
            if category == DataCategory.LIST:
                return parse_list(text), True
            elif category == DataCategory.DICT:
                return parse_dict(text), True
        except Exception:
            return text, False
    elif category == DataCategory.SCALAR:
        is_valid = validate_format(text, rgx)
        return text, is_valid
    else:
        print(f"Warning: Complex structures are not supported for parsing: {text}")
        return str(text), False


def parse_dict(text):
    """
    Parses a string in the format "key1: value1, key2: value2" into a dictionary.

    Parameters:
        text (str): The string to parse.

    Returns:
        dict: A dictionary of key-value pairs.

    Raises:
        ValueError: If the text format does not match the expected key-value structure.
    """
    if not text:
        return {}

    match = re.fullmatch(rf"({DICT_PATTERN})*", text)
    if not match:
        raise ValueError("Invalid dictionary format. Expected 'key1: value1, key2: value2'.")

    pairs = re.findall(DICT_PATTERN, text)

    # Format the returned dict
    return {key: value for key, value in pairs}


def parse_list(text):
    """
    Parses a comma-separated string like 'item1', 'item2' into a list.

    Parameters:
        text (str): The string to parse.

    Returns:
        list: A list of items.

    Raises:
        ValueError: If the string format does not match the expected quoted list structure.
    """
    if not text:
        return []

    match = re.fullmatch(LIST_PATTERN, text)
    if not match:
        raise ValueError("Invalid list format. Expected 'item1', 'item2'.")

    # Format the returned list
    return re.findall(r"['\"](.*?)['\"]", text)


def data_category(item):
    """
    Identifies the data category of an item (SCALAR, LIST, DICT,  or COMPLEX).

    Parameters:
        item: The item to categorize.

    Returns:
        DataCategory: The identified data category.
    """
    if item is None:
        return DataCategory.SCALAR
    elif isinstance(item, (int, float, str, bool)):
        return DataCategory.SCALAR
    elif isinstance(item, list):
        return DataCategory.LIST if all(isinstance(i, (int, float, str, bool)) for i in item) else DataCategory.COMPLEX
    elif isinstance(item, dict):
        return DataCategory.DICT if all(isinstance(v, (int, float, str, bool)) for v in item.values()) else DataCategory.COMPLEX
    else:
        return DataCategory.COMPLEX  # Fallback for unsupported or unknown types


def get_regex(item):
    """
    Provides the regex pattern for matching the format of a given item.

    Parameters:
        item: The data structure to determine the regex for.

    Returns:
        str: The regex pattern for matching the item's format, or None if unsupported.
    """
    value_type = data_category(item)
    if value_type == DataCategory.DICT:
        return DICT_PATTERN
    elif value_type == DataCategory.LIST:
        return LIST_PATTERN
    return None


def validate_format(value, regex):
    """
    Validates if a string fully matches a specified regex pattern.

    Parameters:
        value (str): The string to validate.
        regex (str): The regex pattern to match.

    Returns:
        bool: True if the string matches the regex, False otherwise.
    """
    return bool(re.fullmatch(regex, value)) if value and regex else True
