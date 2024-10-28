from mspy_vendi.core.schemas import BaseSchema


class CreateGeographySchema(BaseSchema):
    name: str
    postcode: str | None
