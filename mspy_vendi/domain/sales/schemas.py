from datetime import date, datetime, time

from pydantic import NonNegativeInt, PositiveInt

from mspy_vendi.core.constants import DEFAULT_SOURCE_SYSTEM
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.core.validators import DecimalFloat
from mspy_vendi.domain.machines.schemas import MachineDetailSchema
from mspy_vendi.domain.products.schemas import ProductDetailSchema


class SaleBaseSchema(BaseSchema):
    sale_date: date
    sale_time: time
    quantity: PositiveInt
    source_system: str = DEFAULT_SOURCE_SYSTEM
    source_system_id: PositiveInt
    product_id: PositiveInt
    machine_id: PositiveInt


class SaleCreateSchema(SaleBaseSchema): ...


class SaleDetailSchema(SaleBaseSchema):
    id: PositiveInt
    product: ProductDetailSchema
    machine: MachineDetailSchema


class BaseQuantitySchema(BaseSchema):
    quantity: NonNegativeInt


class DecimalQuantitySchema(BaseSchema):
    quantity: DecimalFloat


class TimeFrameSalesSchema(BaseQuantitySchema):
    time_frame: datetime


class DecimalTimeFrameSalesSchema(DecimalQuantitySchema):
    time_frame: datetime


class CategoryProductQuantitySchema(BaseQuantitySchema):
    category_name: str


class CategoryTimeFrameSalesSchema(BaseSchema):
    category_name: str
    sale_range: list[TimeFrameSalesSchema]
