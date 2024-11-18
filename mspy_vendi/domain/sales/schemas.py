from datetime import date, datetime, time
from enum import Enum

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


class TimePeriodEnum(Enum):
    MORNING = ("6 AM - 6 PM", time(6, 0, 0), time(17, 59, 59))
    EVENING = ("6 PM - 8 PM", time(18, 0, 0), time(19, 59, 59))
    NIGHT = ("8 PM - 10 PM", time(20, 0, 0), time(21, 59, 59))
    LATE_NIGHT = ("10 PM - 12 AM", time(22, 0, 0), time(23, 59, 59))
    MIDNIGHT = ("12 AM - 2 AM", time(0, 0, 0), time(1, 59, 59))
    EARLY_MORNING = ("2 AM - 6 AM", time(2, 0, 0), time(5, 59, 59))

    @property
    def name(self) -> str:
        return self.value[0]

    @property
    def start(self) -> time:
        return self.value[1]

    @property
    def end(self) -> time:
        return self.value[2]


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


class TimePeriodSalesCountSchema(BaseSchema):
    time_period: str
    sales: NonNegativeInt
