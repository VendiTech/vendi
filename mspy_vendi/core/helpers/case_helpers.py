def to_title_case(field_name: str) -> str:
    """
    Convert field name to a title case.

    Example:
    >>> "use_phone_contact" -> "Use Phone Contact"

    :param field_name: Field name to be converted.

    :return: Converted field name.
    """
    return " ".join([item.capitalize() for item in field_name.split("_")])
