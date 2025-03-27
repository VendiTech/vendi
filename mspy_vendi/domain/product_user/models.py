from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mspy_vendi.core.enums.db import CascadesEnum
from mspy_vendi.db.base import Base, CommonMixin

if TYPE_CHECKING:
    from mspy_vendi.domain.products.models import Product
    from mspy_vendi.domain.user.models import User


class ProductUser(CommonMixin, Base):
    product_id = mapped_column(
        BigInteger,
        ForeignKey(
            "product.id",
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

    product: Mapped["Product"] = relationship(back_populates="product_users", uselist=False)
    user: Mapped["User"] = relationship(back_populates="product_users", uselist=False)

    __table_args__ = (UniqueConstraint("product_id", "user_id", name="uq_product_user_product_id_user_id"),)
