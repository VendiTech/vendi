from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Computed, Enum, String
from sqlalchemy.dialects.postgresql import ARRAY as PGARRAY
from sqlalchemy.orm import Mapped, mapped_column

from mspy_vendi.db.base import Base, CommonMixin
from mspy_vendi.domain.user.enums import (
    PermissionEnum,
    RoleEnum,
    StatusEnum,
    permission_db_enum,
    role_db_enum,
    status_db_enum,
)


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
