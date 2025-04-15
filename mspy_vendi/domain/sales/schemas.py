from datetime import date, datetime, time
from typing import Any

from pydantic import Field, NonNegativeInt, PositiveInt, model_validator

from mspy_vendi.core.constants import DEFAULT_SOURCE_SYSTEM
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.core.validators import DecimalFloat
from mspy_vendi.domain.geographies.schemas import GeographyDetailSchema
from mspy_vendi.domain.machine_impression.schemas import MachineImpressionBulkCreateResponseSchema
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


class ExportSaleDetailSchema(BaseSchema):
    id: PositiveInt = Field(..., alias="Sale ID")
    source_system_name: str = Field(..., alias="Source system name")
    geography: str = Field(..., alias="Geography")
    product_sold: str = Field(..., alias="Product sold")
    product_id: PositiveInt = Field(..., alias="Product ID")
    machine_id: PositiveInt = Field(..., alias="Machine ID")
    machine_name: str = Field(..., alias="Machine Name")
    sale_date: date = Field(..., alias="Date")
    sale_time: time = Field(..., alias="Time")


class PreviousMonthEntityCountSchema(BaseSchema):
    previous_month_statistic: NonNegativeInt | None = None


class PreviousMonthEntityDecimalCountSchema(BaseSchema):
    previous_month_statistic: DecimalFloat | None = None


class BaseQuantitySchema(BaseSchema):
    quantity: NonNegativeInt


class DecimalQuantityBaseSchema(BaseSchema):
    quantity: DecimalFloat


class QuantityStatisticSchema(BaseQuantitySchema, PreviousMonthEntityCountSchema): ...


class DecimalQuantityStatisticSchema(DecimalQuantityBaseSchema, PreviousMonthEntityDecimalCountSchema): ...


class TimeFrameSalesSchema(BaseQuantitySchema):
    time_frame: datetime


class DecimalTimeFrameSalesSchema(DecimalQuantityBaseSchema):
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


class UnitsStatisticSchema(PreviousMonthEntityDecimalCountSchema):
    units: DecimalFloat


class GeographyDecimalQuantitySchema(DecimalQuantityBaseSchema):
    geography: GeographyDetailSchema


class ConversionRateSchema(BaseSchema):
    customers_new: NonNegativeInt = Field(0)
    customers_returning: NonNegativeInt = Field(0)


class VenueSalesQuantitySchema(BaseQuantitySchema):
    venue: str


class SaleDateTimeBaseSchema(BaseSchema):
    sale_date: date
    sale_time: time


class CategoryProductQuantityDateSchema(CategoryProductQuantitySchema, SaleDateTimeBaseSchema):
    product_name: str
    product_id: PositiveInt


class ProductsCountGeographySchema(BaseSchema):
    products: DecimalFloat
    geography: GeographyDetailSchema


class ProductVenueSalesCountSchema(VenueSalesQuantitySchema, SaleDateTimeBaseSchema):
    product_name: str


class ExcelSaleCreateSchema(BaseSchema):
    id: int = Field(..., alias="Transaction ID")
    sale_date_and_time: str = Field(..., alias="Settlement Date and Time (GMT)")
    sale_date: date
    sale_time: time
    quantity: PositiveInt = 1
    source_system: str = "Excel"
    source_system_id: int = Field(..., alias="Transaction ID")
    product_name: str = Field(..., alias="Product Name")
    machine_name: str = Field(..., alias="Machine Name")

    @model_validator(mode="before")
    @classmethod
    def split_settlement_datetime(cls, data: Any) -> Any:
        """
        Split the raw datetime string from Excel into separate `sale_date` and `sale_time` fields.

        If parsing fails, both fields will be set to None.
        """
        raw_value = data.get("Settlement Date and Time (GMT)")

        if raw_value:
            try:
                dt = datetime.strptime(str(raw_value), "%d/%m/%Y %H:%M:%S")
                data["sale_date"] = dt.date()
                data["sale_time"] = dt.time()
            except ValueError:
                data["sale_date"] = None
                data["sale_time"] = None

        return data


class SalesBulkCreateResponseSchema(MachineImpressionBulkCreateResponseSchema): ...
