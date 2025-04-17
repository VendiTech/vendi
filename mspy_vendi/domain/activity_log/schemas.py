from datetime import datetime
from typing import Any

from pydantic import Field, PositiveInt

from mspy_vendi.core.enums import ExportEntityTypeEnum, ExportTypeEnum, ScheduleEnum
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.domain.activity_log.enums import EventTypeEnum


class ActivityLogBasicEventSchema(BaseSchema):
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None


class ActivityLogExportSchema(ActivityLogBasicEventSchema):
    entity_type: ExportEntityTypeEnum | None = None
    schedule: ScheduleEnum | None = None
    export_type: ExportTypeEnum | None = None


class ActivityLogStateDetailSchema(ActivityLogBasicEventSchema):
    permissions: list[str] | None = None
    role: str | None = None
    machine_names: list[str] | None = None
    product_names: list[str] | None = None


class ActivityLogStateSchema(BaseSchema):
    previous_state: ActivityLogStateDetailSchema | None = None
    current_state: ActivityLogStateDetailSchema


class ActivityLogBaseSchema(BaseSchema):
    user_id: PositiveInt | None
    event_type: EventTypeEnum
    event_context: (
        ActivityLogStateDetailSchema | ActivityLogStateSchema | ActivityLogBasicEventSchema | ActivityLogExportSchema
    ) = {}


class ActivityLogDetailSchema(ActivityLogBaseSchema):
    id: PositiveInt
    created_at: datetime


class ExportActivityLogDetailSchema(BaseSchema):
    id: str | PositiveInt = Field(..., alias="ID")
    action: str = Field(..., alias="Action")
    name: str = Field(..., alias="Name")
    date: str = Field(..., alias="Date and time")
    additional_context: dict[str, Any] = Field(..., alias="Additional Context")
