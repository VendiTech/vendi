from typing import Annotated, Any, AsyncGenerator, Callable, Coroutine

from fastapi import Depends, Request, WebSocketException, status
from fastapi.websockets import WebSocket
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from mspy_vendi.api.auth_backend import backend, get_jwt_strategy
from mspy_vendi.config import log
from mspy_vendi.core.exceptions.base_exception import UnauthorizedError
from mspy_vendi.core.helpers.auth_helpers import check_auth_criteria
from mspy_vendi.core.helpers.logging_helpers import get_described_user_info
from mspy_vendi.deps import get_user_db
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.services import AuthUserService


async def get_auth_user_service(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
) -> AsyncGenerator[AuthUserService, None]:
    yield AuthUserService(user_db)


fastapi_users = FastAPIUsers[User, int](get_auth_user_service, [backend])

current_user: dict[str, bool] = dict(active=True, verified=True)
super_user: dict[str, bool] = dict(active=True, verified=True, superuser=True)


async def get_jwt_token(request: Request = None, websocket: WebSocket = None) -> str:
    if request:
        if not (header := request.headers.get("Authorization")):
            raise UnauthorizedError

        return header

    if websocket:
        if not (token := websocket.headers.get("Authorization")):
            if not (token := websocket.query_params.get("token")):
                raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        return token

    raise ValueError("Request or WebSocket must be provided.")


async def parse_jwt_token(
    token: Annotated[str, Depends(get_jwt_token)],
    jwt_strategy: Annotated[JWTStrategy, Depends(get_jwt_strategy)],
    auth_service: Annotated[AuthUserService, Depends(get_auth_user_service)],
) -> User:
    jwt_token: str = token.removeprefix("Bearer ").strip()

    return await jwt_strategy.read_token(token=jwt_token, user_manager=auth_service)  # noqa


def get_current_user(
    is_active: bool = True, is_superuser: bool | None = None, is_verified: bool = True
) -> Callable[[Request, User], Coroutine[Any, Any, User]]:
    async def wrapper(request: Request, user: Annotated[User, Depends(parse_jwt_token)]) -> User:
        check_auth_criteria(
            user,
            is_active,
            is_superuser,
            is_verified,
        )

        log.info("User is authorized.", info=get_described_user_info(user, request=request))
        return user

    return wrapper
