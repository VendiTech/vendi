from datetime import datetime
from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Computed, DateTime, Enum, LargeBinary, String
from sqlalchemy.dialects.postgresql import ARRAY as PGARRAY
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mspy_vendi.core.enums.db import ORMRelationshipCascadeTechniqueEnum
from mspy_vendi.db.base import Base, CommonMixin
from mspy_vendi.domain.user.enums import (
    PermissionEnum,
    RoleEnum,
    StatusEnum,
    permission_db_enum,
    role_db_enum,
    status_db_enum,
)

if TYPE_CHECKING:
    from mspy_vendi.db import ActivityLog, Machine, MachineUser
    from mspy_vendi.domain.product_user.models import ProductUser
    from mspy_vendi.domain.products.models import Product


class User(CommonMixin, SQLAlchemyBaseUserTable[int], Base):
    firstname: Mapped[str] = mapped_column(String(length=100))
    lastname: Mapped[str] = mapped_column(String(length=100))
    company_name: Mapped[str | None] = mapped_column(String(length=100))
    job_title: Mapped[str | None] = mapped_column(String(length=100))
    role: Mapped[Enum] = mapped_column(role_db_enum, default=RoleEnum.USER)
    permissions: Mapped[list[PermissionEnum]] = mapped_column(
        PGARRAY(permission_db_enum), default=[PermissionEnum.READ]
    )
    phone_number: Mapped[str | None]
    status: Mapped[Enum] = mapped_column(status_db_enum, default=StatusEnum.ACTIVE)
    last_logged_in: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_superuser: Mapped[bool] = mapped_column(
        Computed(
            f"""
                CASE
                    WHEN role = {RoleEnum.ADMIN!r} AND {PermissionEnum.ANY!r} = ANY(permissions) THEN true
                    ELSE false
                END
            """,
            persisted=True,
        )
    )

    company_logo_image: Mapped[bytes | None] = mapped_column(LargeBinary)

    machine_users: Mapped[list["MachineUser"]] = relationship(
        back_populates="user", passive_deletes=ORMRelationshipCascadeTechniqueEnum.db_cascade
    )
    machines: AssociationProxy[list["Machine"]] = association_proxy("machine_users", "machine")

    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        back_populates="user", passive_deletes=ORMRelationshipCascadeTechniqueEnum.db_cascade
    )

    product_users: Mapped[list["ProductUser"]] = relationship(
        back_populates="user", passive_deletes=ORMRelationshipCascadeTechniqueEnum.db_cascade
    )
    products: AssociationProxy[list["Product"]] = association_proxy("product_users", "product")
