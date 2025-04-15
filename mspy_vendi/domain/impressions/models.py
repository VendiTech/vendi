from datetime import date
from decimal import Decimal

from sqlalchemy import DECIMAL, Enum, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from mspy_vendi.db.base import Base, CommonMixin
from mspy_vendi.domain.impressions.enums import ImpressionEntityTypeEnum, impression_entity_type_enum


class Impression(CommonMixin, Base):
    device_number: Mapped[str]
    date: Mapped[date]
    total_impressions: Mapped[Decimal] = mapped_column(
        DECIMAL(precision=10, scale=1), comment="Total number of impressions"
    )
    seconds_exposure: Mapped[int] = mapped_column(server_default=text("0"))
    advert_playouts: Mapped[int] = mapped_column(server_default=text("0"))
    source_system: Mapped[str] = mapped_column(String(50), comment="Name of the source system")
    type: Mapped[Enum] = mapped_column(impression_entity_type_enum, default=ImpressionEntityTypeEnum.IMPRESSION)
    source_system_id: Mapped[str] = mapped_column(
        String(),
        comment="""
            ID of the impression in the source system. Combination of the `device_number` and `date`. Must be unique.
        """,
    )

    __table_args__ = (
        Index("idx_impression_device_number", "device_number"),
        UniqueConstraint("source_system_id", "type", name="uq_impression_source_system_id_type"),
    )
