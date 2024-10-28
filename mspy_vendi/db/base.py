from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import ARRAY, DECIMAL, BigInteger, DateTime, Identity, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, declarative_mixin, declared_attr, mapped_column

from mspy_vendi.core.helpers import pascal_to_snake


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    type_annotation_map = {
        list[float]: ARRAY(DECIMAL),
        list[int]: ARRAY(BigInteger),
        list[str]: ARRAY(String),
        dict[str, Any]: JSONB(none_as_null=True),
        list[dict[str, Any]]: JSONB(none_as_null=True),
        UUID: PGUUID,
    }


@declarative_mixin
class CommonMixin:
    repr_cols: tuple[str] | tuple[str, ...] = ("id",)

    id: Mapped[int] = mapped_column(BigInteger, Identity(start=1, cycle=True), primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.current_timestamp(), server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.current_timestamp(), server_onupdate=func.current_timestamp()
    )

    @declared_attr
    def __tablename__(cls):
        return pascal_to_snake(cls.__name__)  # type: ignore

    def __repr__(self) -> str:
        """
        Don't add relationships to the `repr_cols`, because they may lead to unexpected loading
        """
        return f"<{self.__class__.__name__} {', '.join([f'{col}={getattr(self, col)}' for col in self.repr_cols])}>"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert an SQLAlchemy model instance to a dictionary.

        This method converts the given SQLAlchemy model instance to a dictionary representation,
        including attributes such as hybrid properties, properties, and column properties,
        but excluding deferred fields and relationships.

        :return: A dictionary representing the data attributes of the model instance.
        """
        initial_data: dict[str, Any] = {key: value for key, value in self.__dict__.items() if not key.startswith("_")}

        for key, value in self.__class__.__dict__.items():
            if isinstance(value, property) and key not in initial_data:
                initial_data[key] = getattr(self, key)

            elif isinstance(value, hybrid_property) and key not in initial_data:
                initial_data[key] = getattr(self, key)

        return initial_data
