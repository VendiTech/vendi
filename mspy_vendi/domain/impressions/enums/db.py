from sqlalchemy import Enum

from mspy_vendi.domain.impressions.enums.enum import ImpressionEntityTypeEnum

impression_entity_type_enum = Enum(
    *[impression_entity_type.value for impression_entity_type in ImpressionEntityTypeEnum],
    name="impression_entity_type_enum",
)
