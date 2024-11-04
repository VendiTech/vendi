import functools
import inspect
from abc import ABC
from typing import Any, Callable, Generic, TypeVar

from fastapi import APIRouter
from pydantic import BaseModel, PositiveInt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from mspy_vendi.core.enums import ApiTagEnum, CRUDEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.service import CRUDService
from mspy_vendi.db import User

Service = TypeVar("Service", bound=type[CRUDService])
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)
DetailedSchema = TypeVar("DetailedSchema", bound=BaseModel)
Schema = TypeVar("Schema", bound=BaseModel)
PageSchema = TypeVar("PageSchema", bound=BaseModel)
FilterClass = TypeVar("FilterClass", bound=BaseModel)


class CRUDApi(
    ABC,
    Generic[
        Service,
        Schema,
        CreateSchema,
        UpdateSchema,
        DetailedSchema,
        PageSchema,
        FilterClass,
        # UserInfoSchema,
        # Role,
    ],
):
    """
    Base CRUD API class based view
    """

    service: Service
    "The service class that handles business logic for the API."

    schema: Schema
    "The schema used for serialization and validation of API responses."

    detailed_schema: DetailedSchema | Schema
    "The schema used for detailed representation of objects."

    create_schema: CreateSchema | Schema
    "The schema used for input validation when creating new objects."

    update_schema: UpdateSchema | Schema
    "The schema used for input validation when updating existing objects."

    pagination_schema: PageSchema
    "The schema used for pagination responses."

    api_tags: list[ApiTagEnum] = []
    "List of tags for API documentation. Defaults to an empty list."

    get_db_session: Callable[[], AsyncSession]
    "A callable that returns the database session."

    current_user_mapping: dict[CRUDEnum, Callable[[], User]]
    "A callable that checks the current user."

    endpoints: tuple[CRUDEnum, ...] = tuple(CRUDEnum)
    "Tuple defining which CRUD operations are enabled for this API."

    exclude_from_schema: tuple[CRUDEnum, ...] = tuple()
    "Tuple defining which CRUD operations to exclude from the OpenAPI schema."

    path_param_name: str = "obj_id"
    "The name of the path parameter for object IDs."

    path_param_annotation: Any = PositiveInt
    "The annotation for the path parameter. Defaults to ID."

    def __init__(self, api_router: APIRouter):
        self.api_router = api_router

        # Double braces for escaping: https://docs.python.org/3/library/string.html#format-string-syntax
        self.obj_path_param = f"/{{{self.path_param_name}}}"

        if not hasattr(self, "detailed_schema"):
            self.detailed_schema = self.schema

        if not hasattr(self, "create_schema"):
            self.create_schema = self.schema

        if not hasattr(self, "update_schema"):
            self.update_schema = self.create_schema

        if CRUDEnum.LIST in self.endpoints:
            self._fix_method_signature(method_name="list", crud_method=CRUDEnum.LIST)
            self.api_router.add_api_route(
                "",
                self.list,
                methods=["GET"],
                response_model=self.pagination_schema[self.schema],
                summary="Get all objects",
                tags=self.api_tags,
                include_in_schema=CRUDEnum.LIST not in self.exclude_from_schema,
            )

        if CRUDEnum.GET in self.endpoints:
            self._fix_method_signature(method_name="get", crud_method=CRUDEnum.GET)
            self.api_router.add_api_route(
                self.obj_path_param,
                self.get,
                methods=["GET"],
                response_model=self.detailed_schema,
                summary=f"Get object by `{self.path_param_name}`",
                tags=self.api_tags,
                include_in_schema=CRUDEnum.GET not in self.exclude_from_schema,
            )

        if CRUDEnum.CREATE in self.endpoints:
            self._fix_method_signature(method_name="create", crud_method=CRUDEnum.CREATE)
            self.api_router.add_api_route(
                "",
                self.create,
                methods=["POST"],
                response_model=self.schema,
                status_code=status.HTTP_201_CREATED,
                summary="Create object",
                tags=self.api_tags,
                description=self.create.__doc__,
                include_in_schema=CRUDEnum.CREATE not in self.exclude_from_schema,
            )

        if CRUDEnum.UPDATE in self.endpoints:
            self._fix_method_signature(method_name="update", crud_method=CRUDEnum.UPDATE)
            self.api_router.add_api_route(
                self.obj_path_param,
                self.update,
                methods=["PATCH"],
                response_model=self.schema,
                summary=f"Update object by `{self.path_param_name}`",
                tags=self.api_tags,
                description=self.update.__doc__,
                include_in_schema=CRUDEnum.UPDATE not in self.exclude_from_schema,
            )

        if CRUDEnum.DELETE in self.endpoints:
            self._fix_method_signature(method_name="delete", crud_method=CRUDEnum.DELETE)
            self.api_router.add_api_route(
                self.obj_path_param,
                self.delete,
                methods=["DELETE"],
                summary=f"Delete object by `{self.path_param_name}`",
                tags=self.api_tags,
                description=self.delete.__doc__,
                include_in_schema=CRUDEnum.DELETE not in self.exclude_from_schema,
            )

    def _fix_method_signature(self, method_name: str, crud_method: CRUDEnum) -> None:
        """
        FastAPI uses function/method signatures to determine the parameters to inject. Since we don't know the method
        signatures in advance until the abstract class gets converted into a concrete class and is instantiated,
        the method signatures are adapted to the concrete class upon instantiation.

        This method replaces the method signature of the given method with the correct one.

        :param method_name: name of the method to fix
        :return: None

        **Note**
        This method dynamically sets the name and annotation of the path parameter. It checks each parameter to see if
        it matches the name "path_param", used in the endpoint's arguments (like **kwargs). If a match is found, it
        replaces the parameter's name with the specified `path_param_name` attribute of the class, and replaces its
        annotation with the specified `path_param_annotation`.
        """

        method = getattr(self, method_name)
        # Only if the function wasn't already overriden
        if method.__func__ == getattr(CRUDApi, method_name):
            signature = inspect.signature(method)
            # create new signature
            new_parameters = []
            for p in signature.parameters.values():
                if p.annotation == CreateSchema:  # type: ignore
                    p = p.replace(annotation=self.create_schema)
                elif p.annotation == UpdateSchema:  # type: ignore
                    p = p.replace(annotation=self.update_schema)
                elif p.annotation == AsyncSession:
                    p = p.replace(default=self.get_db_session)
                elif p.annotation == User:
                    p = p.replace(default=self.current_user_mapping[crud_method])
                elif p.annotation == FilterClass:  # type: ignore
                    p = p.replace(
                        annotation=self.service.filter_class,
                        default=self.service.filter_depend(self.service.filter_class),
                    )

                # This step is necessary to dynamically set the name and annotation of the path parameter.
                elif p.name == "path_param":
                    p = p.replace(name=self.path_param_name)
                    p = p.replace(annotation=self.path_param_annotation)

                new_parameters.append(p)

            new_signature = signature.replace(parameters=new_parameters)

            # replace function and signature
            new_func = functools.partial(getattr(self, method_name))
            new_func.__signature__ = new_signature  # type: ignore
            new_func.__doc__ = method.__doc__
            setattr(self, method_name, new_func)

    async def list(self, db_session: AsyncSession, query_filter: FilterClass, user: User) -> Page[Schema]:
        """
        Get all objects
        """

        return await self.service(db_session).get_all(query_filter, user=user)

    async def get(self, db_session: AsyncSession, user: User, **path_param: Any) -> Schema:
        """
        Get a single object
        """

        return await self.service(db_session).get(path_param.get(self.path_param_name), user=user)

    async def create(self, obj: CreateSchema, db_session: AsyncSession, user: User) -> Schema:
        """
        Creates a new object
        """

        return await self.service(db_session).create(obj, user=user)

    async def update(self, obj: UpdateSchema, db_session: AsyncSession, user: User, **path_param: Any) -> Schema:
        """
        Updates an object
        """

        return await self.service(db_session).update(path_param.get(self.path_param_name), obj, user=user)

    async def delete(self, db_session: AsyncSession, user: User, **path_param: Any) -> None:
        """
        Deletes an object
        """

        await self.service(db_session).delete(path_param.get(self.path_param_name), user=user)
