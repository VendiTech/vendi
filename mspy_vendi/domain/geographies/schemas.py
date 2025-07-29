from pydantic import PositiveInt

from mspy_vendi.core.schemas import BaseSchema


class GeographyBaseSchema(BaseSchema):
    name: str
    postcode: str | None
    map_location: str | None = None


class GeographyCreateSchema(BaseSchema):
    name: str
    postcode: str | None


class GeographyDetailSchema(GeographyBaseSchema):
    id: PositiveInt
    map_location: str | None = None


class GeographyUpdateSchema(BaseSchema):
    map_location: str | None = None
