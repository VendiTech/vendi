from sqlalchemy import Enum

from .enum import EventTypeEnum

event_type_enum = Enum(
    *[event_type.value for event_type in EventTypeEnum],
    name="event_type_enum",
)
