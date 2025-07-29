from sqlalchemy import Enum

from mspy_vendi.domain.entity_log.enums.enum import EntityTypeEnum

entity_type_enum = Enum(
    *[entity_type.value for entity_type in EntityTypeEnum],
    name="entity_type_enum",
)
