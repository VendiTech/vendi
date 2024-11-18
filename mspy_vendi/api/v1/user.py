from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from pydantic import PositiveInt

from mspy_vendi.core.api import CRUDApi
from mspy_vendi.core.enums import ApiTagEnum, CRUDEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.auth import get_current_user
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.schemas import UserDetail, UserPermissionsModifySchema, UserUpdate
from mspy_vendi.domain.user.services import UserService

router = APIRouter(prefix="/user", default_response_class=ORJSONResponse, tags=[ApiTagEnum.USER])


@router.get("/me", response_model=UserDetail)
async def get__show_me(
    user: Annotated[User, Depends(get_current_user())],
    service: Annotated[UserService, Depends()],
) -> UserDetail:
    """
    Retrieve the User by ID.

    - **user_id**: User ID
    """
    return await service.get(obj_id=user.id)


@router.patch("/edit")
async def update__user(
    updated_obj: UserUpdate,
    user: Annotated[User, Depends(get_current_user())],
    service: Annotated[UserService, Depends()],
) -> UserDetail:
    """
    Update the User by Provided `UserUpdate` object.
    """
    return await service.update(obj_id=user.id, obj=updated_obj)


@router.patch("/permission/add/{user_id}")
async def patch__add_permissions(
    user_id: PositiveInt,
    user_permissions: UserPermissionsModifySchema,
    service: Annotated[UserService, Depends()],
    _: Annotated[User, Depends(get_current_user(is_superuser=True))],
) -> UserDetail:
    """
    Add permissions to the User by ID.

    - **user_id**: User ID
    """
    return await service.add_permission(user_id=user_id, obj=user_permissions)


@router.patch("/permission/delete/{user_id}")
async def patch__delete_permissions(
    user_id: PositiveInt,
    user_permissions: UserPermissionsModifySchema,
    service: Annotated[UserService, Depends()],
    _: Annotated[User, Depends(get_current_user(is_superuser=True))],
) -> UserDetail:
    """
    Drop permission from the User by ID.

    - **user_id**: User ID
    """
    return await service.delete_permissions(user_id=user_id, obj=user_permissions)


class UserAPI(CRUDApi):
    service = UserService
    schema = UserDetail
    get_db_session = Depends(get_db_session)
    current_user_mapping = {
        CRUDEnum.GET: Depends(get_current_user(is_superuser=True)),
        CRUDEnum.LIST: Depends(get_current_user(is_superuser=True)),
    }
    pagination_schema = Page
    endpoints = (CRUDEnum.GET, CRUDEnum.LIST)
    api_tags = (ApiTagEnum.USER,)


UserAPI(router)
