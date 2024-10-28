MAX_NUMBER_OF_CHARACTERS: int = 100
DEFAULT_SOURCE_SYSTEM: str = "Nayax"

SERVER_ERROR_MESSAGE: str = "Something went wrong. Try to use this service later"

# Constants for fastapi-filter library
COMPOUND_SEARCH_FIELD_NAME: str = "search"

DEFAULT_DATE_RANGE_FIELDS: list[str] = ["date_from", "date_to"]
DEFAULT_RANGE_DB_FIELD: str = "created_at"

DEFAULT_AGE_RANGE_DB_FIELD: str = "birthdate"
DEFAULT_AGE_RANGE_FIELDS: list[str] = ["age_from", "age_to"]
