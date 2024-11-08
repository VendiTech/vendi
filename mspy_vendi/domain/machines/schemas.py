from pydantic import PositiveInt

from mspy_vendi.core.schemas import BaseSchema


class MachineBaseSchema(BaseSchema):
    name: str
    geography_id: PositiveInt


class MachineCreateSchema(MachineBaseSchema): ...


class MachineDetailSchema(MachineBaseSchema):
    id: int
