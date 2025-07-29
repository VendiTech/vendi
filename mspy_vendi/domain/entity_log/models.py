from typing import Any

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from mspy_vendi.db.base import Base, CommonMixin
from mspy_vendi.domain.entity_log.enums import entity_type_enum


class EntityLog(CommonMixin, Base):
    entity_type: Mapped[Enum] = mapped_column(entity_type_enum)
    old_value: Mapped[dict[str, Any]] = mapped_column(default={})
    new_value: Mapped[dict[str, Any]] = mapped_column(default={})
