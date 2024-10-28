from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from mspy_vendi.db.base import Base, CommonMixin
from mspy_vendi.domain.user.enums import RoleEnum, StatusEnum, role_db_enum, status_db_enum


class User(CommonMixin, SQLAlchemyBaseUserTable[int], Base):
    firstname: Mapped[str] = mapped_column(String(length=100))
    lastname: Mapped[str] = mapped_column(String(length=100))
    company_name: Mapped[str | None] = mapped_column(String(length=100))
    job_title: Mapped[str | None] = mapped_column(String(length=100))
    role: Mapped[Enum] = mapped_column(role_db_enum, default=RoleEnum.USER)
    phone_number: Mapped[str | None]
    status: Mapped[Enum] = mapped_column(status_db_enum, default=StatusEnum.ACTIVE)
