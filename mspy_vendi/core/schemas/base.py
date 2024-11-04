from datetime import date, datetime
from typing import Annotated, Any
from uuid import UUID

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field, PlainSerializer

from mspy_vendi.core.validators import check_alphanumeric_characters, check_valid_iso_date, convert_to_str_date


class BaseSchema(BaseModel):
    def __hash__(self):
        return hash(tuple(self.model_dump(exclude_unset=True).values()))

    model_config = ConfigDict(
        validate_assignment=True,
        populate_by_name=True,
        from_attributes=True,  # `from_orm` equivalent
    )

    def set_without_validation(self, name: str, value: Any) -> None:
        """
        Workaround to be able to set fields without validation.

        Because due to the validate_assignment=True, we can't set fields without validation.
        And as fact, it raises the RecursionError.
        """
        attr = getattr(self.__class__, name, None)

        if isinstance(attr, property):
            attr.__set__(self, value)
        else:
            self.__dict__[name] = value
            self.__pydantic_fields_set__.add(name)


OptionalFloat = Annotated[float | None, Field(None)]
OptionalString = Annotated[str | None, Field(None)]
OptionalInt = Annotated[int | None, Field(None)]
OptionalDatetime = Annotated[datetime | None, Field(None)]
OptionalBool = Annotated[bool | None, Field(None)]
OptionalUUID = Annotated[UUID | None, Field(None)]

AlphaString = Annotated[str, Field(..., min_length=1, max_length=50), AfterValidator(check_alphanumeric_characters)]

ConstraintString = lambda max_length: Annotated[str | None, Field(None, max_length=max_length, min_length=1)]  # noqa: E731
DateStr = Annotated[
    date,
    BeforeValidator(check_valid_iso_date),
    PlainSerializer(convert_to_str_date, return_type=str),
]
