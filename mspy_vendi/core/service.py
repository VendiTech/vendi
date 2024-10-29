from abc import ABC
from typing import Annotated, Any, Generic, Iterable, TypeVar

from fastapi import Depends
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination import Page
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.core.manager import CRUDManager
from mspy_vendi.deps import get_db_session

Manager = TypeVar("Manager", bound=type[CRUDManager])
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)
Schema = TypeVar("Schema", bound=BaseModel)
PageSchema = TypeVar("PageSchema", bound=Page)


class CRUDService(ABC, Generic[Manager, Schema, CreateSchema, UpdateSchema, PageSchema]):
    """
    CRUD service for SQLAlchemy models.
    """

    manager_class: Manager
    filter_depend: type[FilterDepends] = FilterDepends
    filter_class: type[Filter] = Filter

    def __init__(self, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
        self.manager: Manager = self.manager_class(db_session)
        self.db_session: AsyncSession = db_session

    async def get(self, obj_id: int, *, raise_error: bool = True, **kwargs: Any) -> Schema:
        """
        Get an object by id.

        :param obj_id: Object ID.
        :param raise_error: If True, raises an error if the object is not found.
        :param kwargs: Additional keyword arguments.

        :return: Pydantic model.
        """
        return await self.manager.get(obj_id, raise_error=raise_error, **kwargs)

    async def get_all(self, query_filter: BaseFilter | None = None, **kwargs: Any) -> Page[Schema]:
        """
        Get all objects.

        :param query_filter: Filter object.
        :param kwargs: Additional keyword arguments.

        :return: Paginated result.
        """
        return await self.manager.get_all(query_filter, **kwargs)

    async def get_by_ids(self, obj_ids: Iterable[int], **kwargs: Any) -> list[Schema]:
        """
        Get objects by IDs.

        :param obj_ids: Object IDs.
        :param kwargs: Additional keyword arguments.

        :return: List of Pydantic models.
        """
        return await self.manager.get_by_ids(obj_ids, **kwargs)

    async def create(
        self, obj: CreateSchema, *, obj_id: int | None = None, autocommit: bool = True, **kwargs: Any
    ) -> Schema:
        """
        Creates an entity in the database, and returns the created object.

        :param obj: Pydantic model.
        :param obj_id: Object ID.
        :param autocommit: If True, commits changes to a database, if False - flushes them.
        :param kwargs: Additional keyword arguments.

        :return: Created entity.
        """
        return await self.manager.create(obj, obj_id=obj_id, autocommit=autocommit, **kwargs)

    async def update(self, obj_id: int, obj: UpdateSchema, *, autocommit: bool = True, **kwargs: Any) -> Schema:
        """
        Updates an entity in the database, and returns the updated object.

        :param obj_id: Object ID.
        :param obj: Object to update.
        :param autocommit: If True, commits changes to a database, if False - flushes them.
        :param kwargs: Additional keyword arguments.

        :return: Updated entity.
        """
        return await self.manager.update(obj_id, obj, autocommit=autocommit, **kwargs)

    async def delete(self, obj_id: int, *, autocommit: bool = True, **kwargs: Any) -> None:
        """
        Deletes an entity from the database.

        :param obj_id: Object ID.
        :param autocommit: If True, commits changes to a database, if False - flushes them.
        :param kwargs: Additional keyword arguments.

        :return: None.
        """
        await self.manager.delete(obj_id, autocommit=autocommit, **kwargs)

    async def upsert(self, obj_id: int | None, obj: CreateSchema, *, autocommit: bool = True, **kwargs: Any):
        """
        Updates or creates an entity in the database, and returns the updated or created object.

        :param obj_id: Object ID.
        :param obj: Object to update or create.
        :param autocommit: If True, commits changes to a database, if False-flushes them.
        :param kwargs: Additional keyword arguments.

        :return: Updated or created entity.
        """
        if obj_id and await self.get(obj_id, raise_error=False):
            return await self.update(obj_id, obj, autocommit=autocommit, **kwargs)

        return await self.create(obj, obj_id=obj_id, autocommit=autocommit, **kwargs)
