from pydantic import Field, NonNegativeInt, PositiveInt

from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.domain.geographies.schemas import GeographyDetailSchema


class MachineBaseSchema(BaseSchema):
    name: str = Field(..., alias="machine_name")
    geography_id: PositiveInt


class MachineCreateSchema(MachineBaseSchema): ...


class MachineDetailSchema(MachineBaseSchema):
    id: PositiveInt


class MachinesCountBaseSchema(BaseSchema):
    machines: NonNegativeInt


class MachinesCountGeographySchema(MachinesCountBaseSchema):
    geography: GeographyDetailSchema


class MachinesPerGeographySchema(BaseSchema):
    geography: GeographyDetailSchema
    machines: list[MachineDetailSchema]
