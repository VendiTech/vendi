from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mspy_vendi.db.base import Base, CommonMixin


class Geography(CommonMixin, Base):
    name: Mapped[str] = mapped_column(String(255), comment="Name of the geography")
    postcode: Mapped[str | None] = mapped_column(String(255), comment="Name of the geography")
    map_location: Mapped[str | None] = mapped_column(String(255), comment="Identifier to proper location mapping")

    __table_args__ = (UniqueConstraint("name", name="uq_geography_name"),)
