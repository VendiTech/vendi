from decimal import Decimal

from pydantic import Field

from mspy_vendi.core.constants import DEFAULT_PROJECT_NAME, DEFAULT_TYPE_DATA
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.core.schemas.base import DateStr
from mspy_vendi.domain.impressions.enums import ImpressionEntityTypeEnum


class DataJamDeviceInfoSchema(BaseSchema):
    device: str = Field(..., alias="Device")
    date: str = Field(..., alias="Date")
    total_impressions: Decimal = Field(..., alias="Total")
    seconds_exposure: int = Field(..., alias="avg_temp")
    advert_playouts: int = Field(..., alias="rain")
    type: ImpressionEntityTypeEnum | None = Field(default=ImpressionEntityTypeEnum.IMPRESSION, alias="Field")


class DataJamImpressionSchema(BaseSchema):
    device_info: list[DataJamDeviceInfoSchema]


class DataJamRequestSchema(BaseSchema):
    project_name: str = DEFAULT_PROJECT_NAME
    device_number: str
    start_date: DateStr
    end_date: DateStr
    type_data: str = DEFAULT_TYPE_DATA
