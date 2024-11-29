from datetime import datetime
from typing import Any

from pydantic import PositiveInt

from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.domain.activity_log.enums import EventTypeEnum


class ActivityLogBaseSchema(BaseSchema):
    user_id: PositiveInt | None
    event_type: EventTypeEnum
    event_context: dict[str, Any]


class ActivityLogDetailSchema(ActivityLogBaseSchema):
    id: PositiveInt
    created_at: datetime
