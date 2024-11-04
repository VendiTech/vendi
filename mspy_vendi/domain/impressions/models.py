from datetime import date

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from mspy_vendi.db.base import Base, CommonMixin


class Impression(CommonMixin, Base):
    id: Mapped[str] = mapped_column(String(), primary_key=True)

    date: Mapped[date]
    total_impressions: Mapped[int] = mapped_column(BigInteger, comment="Total number of impressions")
    temperature: Mapped[int]
    rainfall: Mapped[int]
    source_system: Mapped[str] = mapped_column(String(50), comment="Name of the source system")
    source_system_id: Mapped[str] = mapped_column(String(), comment="ID of the impression in the source system")
