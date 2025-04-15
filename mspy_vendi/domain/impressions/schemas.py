import math
from datetime import date as python_date
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import Field, NonNegativeInt, PositiveInt, field_validator, model_validator

from mspy_vendi.core.constants import DEFAULT_SOURCE_SYSTEM
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.core.validators import DecimalFloat
from mspy_vendi.domain.geographies.schemas import GeographyDetailSchema
from mspy_vendi.domain.impressions.enums import ImpressionEntityTypeEnum
from mspy_vendi.domain.machine_impression.schemas import MachineImpressionBulkCreateResponseSchema
from mspy_vendi.domain.sales.schemas import (
    BaseQuantitySchema,
    ConversionRateSchema,
    PreviousMonthEntityCountSchema,
    PreviousMonthEntityDecimalCountSchema,
)


class ImpressionBaseSchema(BaseSchema):
    date: python_date
    total_impressions: Decimal
    type: ImpressionEntityTypeEnum
    seconds_exposure: int
    advert_playouts: int
    source_system: str = DEFAULT_SOURCE_SYSTEM
    source_system_id: str
    device_number: str


class ImpressionCreateSchema(ImpressionBaseSchema): ...


class ImpressionDetailSchema(ImpressionBaseSchema):
    id: PositiveInt


class ExportImpressionDetailSchema(BaseSchema):
    id: PositiveInt = Field(..., alias="Impression ID")
    device_number: str = Field(..., alias="Device Number")
    source_system_name: str = Field(..., alias="Source system name")
    geography: str = Field(..., alias="Geography")
    total_impressions: Decimal = Field(..., alias="Total Impressions")
    machine_id: PositiveInt = Field(..., alias="Machine ID")
    machine_name: str = Field(..., alias="Machine Name")
    date: python_date = Field(..., alias="Date")


class ImpressionCountBaseSchema(BaseSchema):
    impressions: DecimalFloat


class DifferencePercentageBaseSchema(BaseSchema):
    difference: DecimalFloat


class TimeFrameImpressionsSchema(ImpressionCountBaseSchema):
    time_frame: datetime


class GeographyImpressionsCountSchema(ImpressionCountBaseSchema):
    avg_impressions: DecimalFloat
    geography: GeographyDetailSchema


class ExposureBaseSchema(BaseSchema):
    seconds_exposure: NonNegativeInt


class AverageExposureSchema(BaseSchema):
    seconds_exposure: DecimalFloat


class AdvertPlayoutsBaseSchema(BaseSchema):
    advert_playouts: NonNegativeInt


class AdvertPlayoutsStatisticsSchema(AdvertPlayoutsBaseSchema, PreviousMonthEntityCountSchema): ...


class AdvertPlayoutsTimeFrameSchema(AdvertPlayoutsBaseSchema):
    time_frame: datetime


class ExposurePerRangeSchema(ExposureBaseSchema):
    time_frame: datetime


class AverageImpressionsSchema(ImpressionCountBaseSchema, PreviousMonthEntityDecimalCountSchema):
    avg_impressions: DecimalFloat
    total_impressions: DecimalFloat


class TimeFrameImpressionsByVenueSchema(TimeFrameImpressionsSchema):
    venue: str


class ImpressionsSalesPlayoutsConvertions(
    BaseQuantitySchema,
    TimeFrameImpressionsSchema,
    AdvertPlayoutsTimeFrameSchema,
    ConversionRateSchema,
):
    """
    Example of item:
        {
          "customers_new": 0,
          "customers_returning": 0,
          "advert_playouts": 0,
          "impressions": 0,
          "time_frame": "2024-11-29T14:13:19.666Z",
          "quantity": 0
        }
    """


class ExposureStatisticSchema(ExposureBaseSchema, PreviousMonthEntityCountSchema): ...


class ImpressionsBulkCreateResponseSchema(MachineImpressionBulkCreateResponseSchema): ...


class ExcelImpressionCreateSchema(ImpressionCreateSchema):
    device_number: str = Field(..., alias="Device")
    date: python_date = Field(..., alias="Date")
    total_impressions: Decimal = Field(..., alias="Total")
    type: ImpressionEntityTypeEnum = Field(..., alias="Field")
    seconds_exposure: int | None = Field(default=0, alias="Temp( °C )")
    advert_playouts: int | None = Field(default=0, alias="Rain ( in mm)")
    source_system: str | None = Field(default="Excel")
    source_system_id: str | None = None

    @field_validator("seconds_exposure", "advert_playouts", mode="before")
    @classmethod
    def convert_nan_to_zero(cls, v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return 0
        return int(v)

    @model_validator(mode="before")
    @classmethod
    def set_default_source_system_id(cls, data: Any) -> Any:
        if not data.get("source_system_id"):
            device_number = data.get("Device")
            sale_date = data.get("Date")
            if device_number and sale_date:
                data["source_system_id"] = f"{device_number}_{sale_date}"
        return data
