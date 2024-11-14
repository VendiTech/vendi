import math
from typing import Any

from pydantic import Field, NonNegativeInt, PositiveInt, computed_field, field_validator

from mspy_vendi.core.schemas import BaseSchema


class MachineImpressionCreateSchema(BaseSchema):
    machine_id: PositiveInt | None = Field(..., alias="Nayax Code")
    impression_device_number: str | None = Field(..., alias="DJ  NAME")
    name: str | None = Field(None, alias="Venue Name")
    description: str | None = Field(None, alias="Description")

    @field_validator("machine_id", mode="before")
    @classmethod
    def validate_machine_id(cls, v: Any) -> int | None:
        if isinstance(v, float) and math.isnan(v):
            return None

        return abs(int(v))

    @field_validator("impression_device_number", mode="before")
    @classmethod
    def validate_device_number(cls, v: Any) -> str | None:
        if isinstance(v, float) and math.isnan(v):
            return None

        return v


class MachineImpressionBulkCreateResponseSchema(BaseSchema):
    initial_records: NonNegativeInt
    final_records: NonNegativeInt

    @computed_field
    def created_records(self) -> int:
        return self.final_records - self.initial_records
