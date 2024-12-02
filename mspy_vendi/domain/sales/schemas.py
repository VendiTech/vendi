from datetime import date, datetime, time

from pydantic import Field, NonNegativeInt, PositiveInt

from mspy_vendi.core.constants import DEFAULT_SOURCE_SYSTEM
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.core.validators import DecimalFloat
from mspy_vendi.domain.geographies.schemas import GeographyDetailSchema
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


class MonthlyTotalEntityCountBaseSchema(BaseSchema):
    previous_month_statistic: NonNegativeInt


class DecimalMonthlyTotalEntityCountBaseSchema(BaseSchema):
    previous_month_statistic: DecimalFloat


class BaseQuantitySchema(BaseSchema):
    quantity: NonNegativeInt


class DecimalQuantitySchema(DecimalMonthlyTotalEntityCountBaseSchema):
    quantity: DecimalFloat


class TimeFrameSalesSchema(BaseQuantitySchema):
    time_frame: datetime


class DecimalTimeFrameSalesSchema(DecimalQuantitySchema):
    time_frame: datetime


class CategoryProductQuantitySchema(BaseQuantitySchema):
    category_id: PositiveInt
    category_name: str


class CategoryTimeFrameSalesSchema(BaseSchema):
    category_id: PositiveInt
    category_name: str
    sale_range: list[TimeFrameSalesSchema]


class TimePeriodSalesCountSchema(BaseSchema):
    time_period: str
    sales: NonNegativeInt


class TimePeriodSalesRevenueSchema(BaseSchema):
    time_period: str
    revenue: DecimalFloat


class UnitsTimeFrameSchema(BaseSchema):
    units: DecimalFloat
    time_frame: datetime


class GeographyDecimalQuantitySchema(DecimalQuantitySchema):
    geography: GeographyDetailSchema


class ConversionRateSchema(BaseSchema):
    customers_new: NonNegativeInt = Field(0)
    customers_returning: NonNegativeInt = Field(0)


class VenueSalesQuantitySchema(BaseQuantitySchema):
    venue: str


class CategoryProductQuantityDateSchema(CategoryProductQuantitySchema):
    product_name: str
    product_id: PositiveInt
    sale_date: date


class ProductsCountGeographySchema(BaseSchema):
    products: DecimalFloat
    geography: GeographyDetailSchema
