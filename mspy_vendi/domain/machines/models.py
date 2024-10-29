from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mspy_vendi.core.enums.db import CascadesEnum
from mspy_vendi.db.base import Base, CommonMixin

if TYPE_CHECKING:
    from mspy_vendi.domain.geographies.models import Geography


class Machine(CommonMixin, Base):
    name: Mapped[str] = mapped_column(String(255), comment="Name of the machine")
    geography_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "geography.id",
            ondelete=CascadesEnum.CASCADE.value,
            onupdate=CascadesEnum.CASCADE.value,
        ),
    )

    geography: Mapped["Geography"] = relationship(uselist=False)


class MachineUser(CommonMixin, Base):
    machine_id = mapped_column(
        BigInteger,
        ForeignKey(
            "machine.id",
            ondelete=CascadesEnum.CASCADE.value,
            onupdate=CascadesEnum.CASCADE.value,
        ),
    )
    user_id = mapped_column(
        BigInteger,
        ForeignKey(
            "user.id",
            ondelete=CascadesEnum.CASCADE.value,
            onupdate=CascadesEnum.CASCADE.value,
        ),
    )

    __table_args__ = (UniqueConstraint("machine_id", "user_id", name="uq_machine_user_machine_id_user_id"),)