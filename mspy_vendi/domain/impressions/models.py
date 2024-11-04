from datetime import date

from sqlalchemy import BigInteger, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mspy_vendi.db.base import Base, CommonMixin


class Impression(CommonMixin, Base):
    device_number: Mapped[str]
    date: Mapped[date]
    total_impressions: Mapped[int] = mapped_column(BigInteger, comment="Total number of impressions")
    temperature: Mapped[int]
    rainfall: Mapped[int]
    source_system: Mapped[str] = mapped_column(String(50), comment="Name of the source system")
    source_system_id: Mapped[str] = mapped_column(
        String(),
        comment="""
            ID of the impression in the source system. Combination of the `device_number` and `date`. Must be unique.
        """,
    )

    __table_args__ = (
        Index("idx_impression_device_number", "device_number"),
        UniqueConstraint("source_system_id", name="uq_impression_source_system_id"),
    )
