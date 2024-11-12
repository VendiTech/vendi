from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Annotated, Any

from pydantic import HttpUrl, field_validator
from pydantic.functional_serializers import PlainSerializer
from pydantic_core.core_schema import ValidationInfo

StrLink = Annotated[HttpUrl, PlainSerializer(str, return_type=str)]


def format_decimal(initial_value: Decimal) -> float:
    """
    Format the initial value to have a scale of 2.

    :param initial_value: The initial value to format.

    :return: The formatted value with a scale of 2.
    """
    return float(initial_value.quantize(Decimal("0.0"), rounding=ROUND_HALF_UP))


DecimalFloat = Annotated[Decimal, PlainSerializer(format_decimal, return_type=float)]


def validate_password(field_name: str = "password") -> classmethod:
    """
    Created a field validator that validates ``field_name`` based on password requirements.

    Use this validator in Pydantic models to enforce the correct validation logic.

    :param field_name: Name of the field to validate.

    :return: Сlassmethod representing the Pydantic field validator.
             The field validator is applied to specific ``field_name`` field.

    :raises ValueError: if any of the specified fields in the model were skipped.
    """

    def inner(cls, value: str, values: ValidationInfo) -> str:  # pylint: disable=unused-argument
        errors = []

        if not 8 <= len(value) <= 128:
            errors.append("Password should be at least 8 and maximum 128 characters.")
        if not all(char.isascii() or char.isprintable() for char in value):
            errors.append("Password must contain only ASCII or printable Unicode characters.")
        if any(char.isspace() for char in value):
            errors.append("Password must not contain spaces at the beginning or end.")
        if value == values.data.get("email"):
            errors.append("Password cannot be the same as the email.")

        if errors:
            raise ValueError(errors)

        return value

    return field_validator(field_name)(inner)  # type: ignore


def check_alphanumeric_characters(value: str) -> str:
    """
    Check if the value contains only alphanumeric characters.

    :param value: The value to check.

    :return: The value if it contains only alphanumeric characters.

    :raises ValueError: If the value contains non-alphanumeric characters.
    """
    if not value.isalpha():
        raise ValueError("The value should contain only alphabetic characters.")

    return value


def check_valid_iso_date(date: Any) -> str:
    """
    Try to convert a string to ISO 8601 format.

    :param date: The string object to be converted.

    :return: The string representation in ISO 8601
    """
    try:
        # Attempt to create a datetime object
        datetime.fromisoformat(str(date))
    except ValueError:
        raise ValueError("Invalid ISO date format")

    return date


def convert_to_str_date(date: Any) -> str:
    """
    Try to convert a string to Date format.

    :param date: The string object to be converted.

    :return: The string representation in ISO 8601
    """
    try:
        # Attempt to create a datetime object
        return datetime.fromisoformat(str(date)).strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid Str date format")
