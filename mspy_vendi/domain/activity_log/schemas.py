from datetime import datetime

from pydantic import PositiveInt

from mspy_vendi.core.enums import ExportEntityTypeEnum, ExportTypeEnum, ScheduleEnum
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.domain.activity_log.enums import EventTypeEnum


class ActivityLogBasicEventSchema(BaseSchema):
    firstname: str
    lastname: str
    email: str


class ActivityLogExportSchema(ActivityLogBasicEventSchema):
    entity_type: ExportEntityTypeEnum
    schedule: ScheduleEnum
    export_type: ExportTypeEnum


class ActivityLogStateDetailSchema(ActivityLogBasicEventSchema):
    permissions: list[str]
    role: str
    machine_ids: list[int]


class ActivityLogStateSchema(BaseSchema):
    previous_state: ActivityLogStateDetailSchema
    current_state: ActivityLogStateDetailSchema


class ActivityLogBaseSchema(BaseSchema):
    user_id: PositiveInt | None
    event_type: EventTypeEnum
    event_context: ActivityLogStateDetailSchema | ActivityLogStateSchema | ActivityLogBasicEventSchema = {}


class ActivityLogDetailSchema(ActivityLogBaseSchema):
    id: PositiveInt
    created_at: datetime
