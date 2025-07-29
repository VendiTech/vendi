from typing import Any

from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.domain.entity_log.enums import EntityTypeEnum


class EntityLogBaseSchema(BaseSchema):
    entity_type: EntityTypeEnum
    old_value: dict[str, Any]
    new_value: dict[str, Any]


class EntityLogCreateSchema(EntityLogBaseSchema): ...
