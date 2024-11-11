from pydantic import PositiveInt

from mspy_vendi.core.schemas import BaseSchema


class GeographyBaseSchema(BaseSchema):
    name: str
    postcode: str | None


class GeographyCreateSchema(GeographyBaseSchema): ...


class GeographyDetailSchema(GeographyBaseSchema):
    id: PositiveInt
