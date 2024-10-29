from abc import ABC
from typing import Any, Generic, Sequence, TypeVar

from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import BaseModel
from sqlalchemy import Select, delete, inspect, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.roles import ColumnsClauseRole

from mspy_vendi.core.exceptions.base_exception import BadRequestError, NotFoundError, raise_db_error

Model = TypeVar("Model", bound=type[DeclarativeBase])
CreateSchema = TypeVar("CreateSchema", BaseModel, dict)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)
Schema = TypeVar("Schema", bound=BaseModel)
PageSchema = TypeVar("PageSchema", bound=Page)


class CRUDManager(ABC, Generic[Model, Schema, CreateSchema, UpdateSchema, PageSchema]):
    """
    Base manager class for CRUD operations.
    """

    sql_model: Model

    def __init__(self, session: AsyncSession):
        self.session = session

    def get_query(self) -> Select:
        """
        Returns a query object for the model.

        :return: Query object.
        """
        return select(self.sql_model)

    async def get_all(
        self,
        query_filter: Filter | None = None,
        raw_result: bool = False,
        is_unique: bool = False,
        **_: Any,
    ) -> Page[Schema] | list[Model]:  # type: ignore
        """
        This method retrieves all objects from the database.

        :param query_filter: A SQLAlchemy Filter object to filter the objects to be retrieved. If None, no filter will
                             be applied. Default is None.
        :param raw_result: A flag that determines whether to return a list of raw results without pagination.
                           If True, a list of raw results will be returned.
                           If False, a Page object with paginated results will be returned. Default is False.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.

        :return: A Page object with paginated results if raw_result is False, otherwise a list of raw results.

        :raises NoResultFound: If no objects are found in the database.
        """
        stmt = self.get_query()

        if query_filter:
            stmt = query_filter.filter(stmt)
            stmt = query_filter.sort(stmt)

        if raw_result:
            if is_unique:
                return (await self.session.execute(stmt)).unique().all()  # type: ignore

            return (await self.session.scalars(stmt)).all()  # type: ignore

        return await paginate(self.session, stmt)

    async def get(self, obj_id: int, *, raise_error: bool = True, **_: Any) -> Model | None:
        """
        This method retrieves an object from the database using its ID.

        :param obj_id: The ID of the object to be retrieved.
        :param raise_error: A flag that determines whether an error should be raised if the object is not found.
                            If True, a NotFoundError will be raised when the object is not found.
                            If False, the method will return None when the object is not found. Default is True.

        :return: The retrieved object if it exists. If the object does not exist and raise_error is False, the method
                 will return None.

        :raises NotFoundError: If raise_error is True and the object is not found in the database.
        """
        stmt = self.get_query().where(self.sql_model.id == obj_id)

        if not (result := await self.session.scalar(stmt)) and raise_error:
            raise NotFoundError(detail=f"{self.sql_model.__name__} object with {obj_id=} not found")

        return result

    async def get_by_ids(self, obj_ids: Sequence[int]) -> list[Model]:
        """
        Returns a list of objects by their IDs.

        :param obj_ids: List of IDs.
        :param kwargs: Additional keyword arguments.

        :return: List of objects.
        """
        stmt = self.get_query().where(self.sql_model.id.in_(obj_ids))

        return (await self.session.scalars(stmt)).all()  # type: ignore

    async def _apply_changes(
        self,
        stmt,
        obj_id: int | None = None,
        *,
        is_unique: bool = False,
        autocommit: bool = False,
    ) -> Model:
        """
        Internal method to store changes in DB.
        """
        try:
            result = await self.session.execute(stmt)

            if is_unique:
                result = result.unique()

            result = result.scalar_one()

            if autocommit:
                await self.session.commit()
            else:
                await self.session.flush()

            await self.session.refresh(result)

        except DBAPIError as ex:
            await self.session.rollback()
            raise_db_error(ex)

        except NoResultFound:
            raise NotFoundError(detail=f"{self.sql_model.__name__} object with obj_id={str(obj_id)} not found")

        return result

    async def create(
        self,
        obj: CreateSchema,
        *,
        obj_id: int | None = None,
        autocommit: bool = True,
        is_unique: bool = False,
        **_: Any,
    ) -> Model:
        """
        Creates an entity in the database and returns the created object.

        :param obj: The object to create.
        :param obj_id: The ID of the object to create.
        :param autocommit: If True, commit changes immediately, otherwise flush changes.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.

        :return: The created object.
        """
        create_model: dict[str, Any] = (
            obj.model_dump() | {"id": obj_id}  # type: ignore
            if obj_id
            else obj.model_dump()
            if isinstance(obj, BaseModel)
            else obj
        )

        stmt = insert(self.sql_model).values(**create_model).returning(self.sql_model)

        return await self._apply_changes(stmt=stmt, autocommit=autocommit, is_unique=is_unique)

    async def update(
        self,
        obj_id: int,
        obj: UpdateSchema,
        autocommit: bool = True,
        is_unique: bool = False,
        **_: Any
    ) -> Model:
        """
        Updates an object.

        :param obj: The object to update.
        :param obj_id: The ID of the object to update.
        :param autocommit: If True, commit changes immediately, otherwise flush changes.
        :param is_unique: If True, apply unique filtering to the objects, otherwise do nothing.
        :param kwargs: Additional keyword arguments.

        :returns: The updated object.
        """
        if not (updated_model := obj.model_dump(exclude_defaults=True)):
            raise BadRequestError("No data provided for updating")

        stmt = (
            update(self.sql_model).where(self.sql_model.id == obj_id).values(**updated_model).returning(self.sql_model)
        )

        return await self._apply_changes(stmt=stmt, obj_id=obj_id, autocommit=autocommit, is_unique=is_unique)

    async def delete(self, obj_id: int, autocommit: bool = True, **_: Any) -> None:
        """
        Delete an object.

        :param obj_id: The ID of the object to delete.
        :param autocommit: If True, commit changes immediately, otherwise flush changes.

        :raises DBAPIError: If there is an error during database operations.
        :raises NotFoundError: If item does not exist in a database.
        """
        await self.get(obj_id=obj_id)

        stmt = delete(self.sql_model).where(self.sql_model.id == obj_id)

        try:
            await self.session.execute(stmt)

            if autocommit:
                await self.session.commit()
            else:
                await self.session.flush()

        except DBAPIError as ex:
            await self.session.rollback()
            raise_db_error(ex)

    def get_select_entities(self, exclude_columns: list[str] | None = None) -> list[ColumnsClauseRole]:
        """
        Returns a list of SQLAlchemy column entities to be used in a SELECT statement.

        The method inspects the model's columns and constructs a list of SQLAlchemy column entities.
        It excludes the specified columns if provided.

        :param exclude_columns: Columns to be excluded from the result.

        :return: A list of SQLAlchemy column entities.
        """
        exclude_columns = set(exclude_columns or [])

        mapper = inspect(self.sql_model)

        return [
            getattr(self.sql_model, entity.key)
            for entity in mapper.c
            if entity.key not in exclude_columns  # type: ignore
        ]

    async def get_or_create(self, obj: CreateSchema, obj_id: int | None = None) -> tuple[Schema, bool]:
        """
        Get or create an entity in the database, and returns the DB object.

        :param obj: Pydantic `CreateSchema` model.
        :param obj_id: Object ID.

        :return: tuple of boolean and created entity.
        """
        if result := await self.get(obj_id, raise_error=False):
            return result, False

        return await self.create(obj, obj_id=obj_id), True
