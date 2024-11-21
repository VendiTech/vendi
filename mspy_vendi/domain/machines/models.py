from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mspy_vendi.core.enums.db import CascadesEnum, ORMRelationshipCascadeTechniqueEnum
from mspy_vendi.db.base import Base, CommonMixin

if TYPE_CHECKING:
    from mspy_vendi.domain.geographies.models import Geography
    from mspy_vendi.domain.sales.models import Sale
    from mspy_vendi.domain.user.models import User


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
    sales: Mapped["Sale"] = relationship(
        back_populates="machine",
        passive_deletes=ORMRelationshipCascadeTechniqueEnum.all.value,
    )

    machine_users: Mapped[list["MachineUser"]] = relationship(
        back_populates="machine", passive_deletes=ORMRelationshipCascadeTechniqueEnum.db_cascade
    )


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

    machine: Mapped["Machine"] = relationship(back_populates="machine_users", uselist=False)
    user: Mapped["User"] = relationship(back_populates="machine_users", uselist=False)

    __table_args__ = (UniqueConstraint("machine_id", "user_id", name="uq_machine_user_machine_id_user_id"),)
