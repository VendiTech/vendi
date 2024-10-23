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


def to_title_case(field_name: str) -> str:
    """
    Convert field name to a title case.

    Example:
    >>> "use_phone_contact" -> "Use Phone Contact"

    :param field_name: Field name to be converted.

    :return: Converted field name.
    """
    return " ".join([item.capitalize() for item in field_name.split("_")])
