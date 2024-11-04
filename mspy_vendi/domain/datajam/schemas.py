from pydantic import Field

from mspy_vendi.core.constants import DEFAULT_PROJECT_NAME, DEFAULT_TYPE_DATA
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.core.schemas.base import DateStr


class DataJamDeviceInfoSchema(BaseSchema):
    device: str = Field(..., alias="Device")
    date: str = Field(..., alias="Date")
    total_impressions: int = Field(..., alias="Total")
    temperature: int = Field(..., alias="avg_temp")
    rainfall: int = Field(..., alias="rain")


class DataJamImpressionSchema(BaseSchema):
    device_info: list[DataJamDeviceInfoSchema]


class DataJamRequestSchema(BaseSchema):
    project_name: str = DEFAULT_PROJECT_NAME
    device_number: str
    start_date: DateStr
    end_date: DateStr
    type_data: str = DEFAULT_TYPE_DATA
