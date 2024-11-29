from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from mspy_vendi.core.enums.db import CascadesEnum
from mspy_vendi.db.base import Base, CommonMixin
from mspy_vendi.domain.activity_log.enums.db import event_type_enum

if TYPE_CHECKING:
    from mspy_vendi.db import User


class ActivityLog(CommonMixin, Base):
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "user.id",
            ondelete=CascadesEnum.SET_NULL.value,
            onupdate=CascadesEnum.CASCADE.value,
        ),
    )
    event_type: Mapped[Enum] = mapped_column(event_type_enum)
    event_context: Mapped[dict[str, Any]] = mapped_column(default={})

    user: Mapped["User"] = relationship(back_populates="activity_logs", lazy="joined", uselist=False)

    __table_args__ = (Index("ix_activity_log_user_id", "user_id"),)
