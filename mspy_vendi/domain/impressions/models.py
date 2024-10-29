from datetime import date

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from mspy_vendi.core.enums.db import CascadesEnum
from mspy_vendi.db.base import Base, CommonMixin


class Impression(CommonMixin, Base):
    date: Mapped[date]
    total_impressions: Mapped[int] = mapped_column(BigInteger, comment="Total number of impressions")
    temperature: Mapped[int]
    rainfall: Mapped[int]
    source_system: Mapped[str] = mapped_column(String(50), comment="Name of the source system")
    source_system_id: Mapped[int] = mapped_column(BigInteger, comment="ID of the impression in the source system")

    machine_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "machine.id",
            ondelete=CascadesEnum.CASCADE.value,
            onupdate=CascadesEnum.CASCADE.value,
        ),
    )
