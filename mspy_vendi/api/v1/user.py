from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import ORJSONResponse
from pydantic import PositiveInt

from mspy_vendi.core.api import CRUDApi
from mspy_vendi.core.enums import ApiTagEnum, CRUDEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.auth import get_auth_user_service, get_current_user
from mspy_vendi.domain.machine_user.service import MachineUserService
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.schemas import (
    UserAdminCreateSchema,
    UserAdminEditSchema,
    UserDetail,
    UserPermissionsModifySchema,
    UserUpdate,
)
from mspy_vendi.domain.user.services import AuthUserService, UserService

router = APIRouter(prefix="/user", default_response_class=ORJSONResponse)


@router.get("/me", response_model=UserDetail, tags=[ApiTagEnum.USER])
async def get__show_me(
    user: Annotated[User, Depends(get_current_user(is_verified=None))],
    service: Annotated[UserService, Depends()],
) -> UserDetail:
    """
    Retrieve the User by ID.

    - **user_id**: User ID
    """
    return await service.get(obj_id=user.id)


@router.patch("/edit", tags=[ApiTagEnum.USER])
async def update__user(
    updated_obj: UserUpdate,
    user: Annotated[User, Depends(get_current_user())],
    service: Annotated[UserService, Depends()],
) -> UserDetail:
    """
    Update the User by Provided `UserUpdate` object.
    """
    return await service.update(obj_id=user.id, obj=updated_obj)


@router.patch("/permission/add/{user_id}", tags=[ApiTagEnum.ADMIN_USER])
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


@router.patch("/permission/delete/{user_id}", tags=[ApiTagEnum.ADMIN_USER])
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


@router.delete("/admin/{obj_id}", status_code=status.HTTP_204_NO_CONTENT, tags=[ApiTagEnum.ADMIN_USER])
async def delete__user(
    user_id: PositiveInt,
    service: Annotated[UserService, Depends()],
    _: Annotated[User, Depends(get_current_user(is_superuser=True))],
):
    return await service.delete(obj_id=user_id)


@router.post("/admin/reset-password/{user_id}", status_code=status.HTTP_202_ACCEPTED, tags=[ApiTagEnum.ADMIN_USER])
async def post__reset_password(
    request: Request,
    user_id: PositiveInt,
    user_service: Annotated[UserService, Depends()],
    auth_service: Annotated[AuthUserService, Depends(get_auth_user_service)],
    _: Annotated[User, Depends(get_current_user(is_superuser=True))],
):
    user = await user_service.get(obj_id=user_id)

    return await auth_service.forgot_password(user, request)


@router.post("/admin/create", response_model=UserDetail, tags=[ApiTagEnum.ADMIN_USER])
async def post__create_user(
    user_obj: UserAdminCreateSchema,
    machine_user_service: Annotated[MachineUserService, Depends()],
    auth_service: Annotated[AuthUserService, Depends(get_auth_user_service)],
    _: Annotated[User, Depends(get_current_user(is_superuser=True))],
) -> UserDetail:
    created_user = await auth_service.create(user_obj)  # type: ignore
    await machine_user_service.update_user_machines(created_user.id, *user_obj.machines)

    return await auth_service.get(created_user.id)


@router.patch("/admin/edit/{user_id}", response_model=UserDetail, tags=[ApiTagEnum.ADMIN_USER])
async def patch__edit_user(
    user_id: PositiveInt,
    user_obj: UserAdminEditSchema,
    machine_user_service: Annotated[MachineUserService, Depends()],
    user_service: Annotated[UserService, Depends()],
    _: Annotated[User, Depends(get_current_user(is_superuser=True))],
) -> UserDetail:
    await user_service.update(user_id, user_obj, raise_error=False)  # type: ignore

    if user_obj.machines is not None:
        await machine_user_service.update_user_machines(user_id, *user_obj.machines)

    return await user_service.get(user_id)


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
