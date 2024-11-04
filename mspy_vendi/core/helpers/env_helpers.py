from typing import Any


def boolify(value: Any) -> bool:
    """
    Converts a value into a boolean representation.

    :param value: The value to convert

    :return: Boolean value
    """
    false_strings: list[str] = [
        "f",
        "false",
        "0",
        "[]",
        "{}",
        "0.0",
        "null",
        "none",
        "",
    ]

    return str(value).lower() not in false_strings
