from datetime import date, datetime
from decimal import Decimal

from pydantic import NonNegativeInt, PositiveInt

from mspy_vendi.core.constants import DEFAULT_SOURCE_SYSTEM
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.core.validators import DecimalFloat
from mspy_vendi.domain.geographies.schemas import GeographyDetailSchema


class ImpressionBaseSchema(BaseSchema):
    date: date
    total_impressions: Decimal
    temperature: int
    rainfall: int
    source_system: str = DEFAULT_SOURCE_SYSTEM
    source_system_id: str
    device_number: str


class ImpressionCreateSchema(ImpressionBaseSchema): ...


class ImpressionDetailSchema(ImpressionBaseSchema):
    id: PositiveInt


class ImpressionCountBaseSchema(BaseSchema):
    impressions: NonNegativeInt


class TimeFrameImpressionsSchema(ImpressionCountBaseSchema):
    time_frame: datetime


class GeographyImpressionsCountSchema(ImpressionCountBaseSchema):
    geography: GeographyDetailSchema


class GeographyDecimalImpressionsCountSchema(GeographyImpressionsCountSchema):
    impressions: DecimalFloat


class GeographyDecimalImpressionTimeFrameSchema(BaseSchema):
    time_frame: datetime
    geographies: list[GeographyDecimalImpressionsCountSchema]


class ExposureBaseSchema(BaseSchema):
    seconds_exposure: NonNegativeInt


class AdvertPlayoutsBaseSchema(BaseSchema):
    advert_playouts: NonNegativeInt


class ExposurePerRangeSchema(ExposureBaseSchema):
    time_frame: datetime


class AverageImpressionsSchema(BaseSchema):
    avg_impressions: DecimalFloat
    total_impressions: NonNegativeInt
