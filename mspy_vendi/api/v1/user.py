from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError

from mspy_vendi.core.api import CRUDApi
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.enums import CRUDEnum
from mspy_vendi.domain.user.models import User

from mspy_vendi.domain.user.schemas import UserDetail, UserUpdate
from mspy_vendi.domain.user.services import UserService
from mspy_vendi.core.enums import ApiTagEnum
from mspy_vendi.deps import get_db_session
from mspy_vendi.domain.auth import get_current_user

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

class UserAPI(CRUDApi):
    service = UserService
    schema = UserDetail
    update_schema = UserUpdate
    get_db_session = Depends(get_db_session)
    current_user_mapping = {
        CRUDEnum.GET: Depends(get_current_user(is_superuser=True)),
        CRUDEnum.LIST: Depends(get_current_user(is_superuser=True)),
        CRUDEnum.UPDATE: Depends(get_current_user()),
    }
    pagination_schema = Page
    endpoints = (CRUDEnum.GET, CRUDEnum.LIST, CRUDEnum.UPDATE)
    api_tags = (ApiTagEnum.USER, )


UserAPI(router)
