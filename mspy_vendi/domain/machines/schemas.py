from pydantic import PositiveInt

from mspy_vendi.core.schemas import BaseSchema


class CreateMachineSchema(BaseSchema):
    name: str
    geography_id: PositiveInt
