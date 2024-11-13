from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mspy_vendi.core.enums.db import CascadesEnum, ORMRelationshipCascadeTechniqueEnum
from mspy_vendi.db.base import Base, CommonMixin

if TYPE_CHECKING:
    from mspy_vendi.domain.product_category.models import ProductCategory
    from mspy_vendi.domain.sales.models import Sale


class Product(CommonMixin, Base):
    name: Mapped[str] = mapped_column(String(255), comment="Name of the product")
    price: Mapped[Decimal] = mapped_column(DECIMAL(precision=10, scale=2))

    product_category_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "product_category.id",
            ondelete=CascadesEnum.CASCADE.value,
            onupdate=CascadesEnum.CASCADE.value,
        ),
    )

    product_category: Mapped["ProductCategory"] = relationship(uselist=False)
    sales: Mapped[list["Sale"]] = relationship(
        back_populates="product",
        passive_deletes=ORMRelationshipCascadeTechniqueEnum.all.value,
    )
