from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mspy_vendi.core.enums.db import CascadesEnum, ORMRelationshipCascadeTechniqueEnum
from mspy_vendi.db.base import Base, CommonMixin

if TYPE_CHECKING:
    from mspy_vendi.domain.machines.models import Machine
    from mspy_vendi.domain.products.models import Product


class Sale(CommonMixin, Base):
    sale_date: Mapped[date]
    sale_time: Mapped[time]
    quantity: Mapped[int]
    source_system: Mapped[str] = mapped_column(String(50), comment="Name of the source system")
    source_system_id: Mapped[int] = mapped_column(BigInteger, comment="ID of the sale in the source system")

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "product.id",
            ondelete=CascadesEnum.CASCADE.value,
            onupdate=CascadesEnum.CASCADE.value,
        ),
    )
    machine_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "machine.id",
            ondelete=CascadesEnum.CASCADE.value,
            onupdate=CascadesEnum.CASCADE.value,
        ),
    )

    product: Mapped["Product"] = relationship(
        back_populates="sales",
        uselist=False,
        passive_deletes=ORMRelationshipCascadeTechniqueEnum.all.value,
    )
    machine: Mapped["Machine"] = relationship(
        back_populates="sales",
        uselist=False,
        passive_deletes=ORMRelationshipCascadeTechniqueEnum.all.value,
    )
