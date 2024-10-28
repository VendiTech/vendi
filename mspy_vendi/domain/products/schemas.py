from decimal import Decimal

from pydantic import PositiveInt

from mspy_vendi.core.schemas import BaseSchema


class CreateProductSchema(BaseSchema):
    name: str
    price: Decimal
    product_category_id: PositiveInt
