from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from mspy_vendi.db.base import Base, CommonMixin


class ProductCategory(CommonMixin, Base):
    name: Mapped[str] = mapped_column(String(255), comment="Name of the product category")
