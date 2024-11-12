from decimal import Decimal

from pydantic import PositiveInt

from mspy_vendi.core.schemas import BaseSchema


class ProductBaseSchema(BaseSchema):
    name: str
    price: Decimal
    product_category_id: PositiveInt


class ProductCreateSchema(ProductBaseSchema): ...


class ProductDetailSchema(ProductBaseSchema):
    id: PositiveInt
