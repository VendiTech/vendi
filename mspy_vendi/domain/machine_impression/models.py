from sqlalchemy import BigInteger, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from mspy_vendi.core.enums.db import CascadesEnum
from mspy_vendi.db.base import Base, CommonMixin


class MachineImpression(CommonMixin, Base):
    name: Mapped[str | None]
    description: Mapped[str | None]

    machine_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "machine.id",
            ondelete=CascadesEnum.CASCADE.value,
            onupdate=CascadesEnum.CASCADE.value,
        ),
    )
    impression_device_number: Mapped[str] = mapped_column(
        comment="Identifier of the `device_number` that stored in impression table"
    )

    __table_args__ = (
        Index("idx_machine_impression_machine_id", "machine_id"),
        Index("idx_machine_impression_impression_device_number", "impression_device_number"),
    )
