from datetime import date, datetime
from decimal import Decimal

from pydantic import NonNegativeInt, PositiveInt

from mspy_vendi.core.constants import DEFAULT_SOURCE_SYSTEM
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.core.validators import DecimalFloat
from mspy_vendi.domain.geographies.schemas import GeographyDetailSchema
from mspy_vendi.domain.sales.schemas import BaseQuantitySchema, ConversionRateSchema, PreviousMonthEntityCountSchema


class ImpressionBaseSchema(BaseSchema):
    date: date
    total_impressions: Decimal
    seconds_exposure: int
    advert_playouts: int
    source_system: str = DEFAULT_SOURCE_SYSTEM
    source_system_id: str
    device_number: str


class ImpressionCreateSchema(ImpressionBaseSchema): ...


class ImpressionDetailSchema(ImpressionBaseSchema):
    id: PositiveInt


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


class AdvertPlayoutsTimeFrameSchema(BaseSchema):
    advert_playouts: NonNegativeInt
    time_frame: datetime


class ExposurePerRangeSchema(ExposureBaseSchema):
    time_frame: datetime


class AverageImpressionsSchema(BaseSchema):
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
