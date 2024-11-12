from typing import Annotated, Any, AsyncGenerator, Callable, Coroutine, Generic

from fastapi import APIRouter, Depends, Request
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from mspy_vendi.api.auth_backend import backend, get_jwt_strategy
from mspy_vendi.config import config, log
from mspy_vendi.core.email import MailGunService
from mspy_vendi.core.exceptions.base_exception import UnauthorizedError
from mspy_vendi.core.helpers.auth_helpers import check_auth_criteria
from mspy_vendi.core.helpers.logging_helpers import get_described_user_info
from mspy_vendi.deps import get_email_service, get_user_db
from mspy_vendi.domain.auth.routers.auth_router import get_auth_router
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.services import AuthUserService


async def get_auth_user_service(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
    email_service: Annotated[MailGunService, Depends(get_email_service)],
) -> AsyncGenerator[AuthUserService, None]:
    yield AuthUserService(user_db, email_service)


class CustomFastAPIUsers(FastAPIUsers, Generic[models.UP, models.ID]):  # type: ignore
    def get_auth_router(self, auth_backend: AuthenticationBackend, requires_verification: bool = False) -> APIRouter:
        """
        Return an auth router for a given authentication backend.

        :param auth_backend: The authentication backend instance.
        :param requires_verification: Whether the authentication
        require the user to be verified or not. Defaults to False.
        """
        return get_auth_router(
            auth_backend,
            self.get_user_manager,
            self.authenticator,
            requires_verification,
        )


fastapi_users = CustomFastAPIUsers[User, int](get_auth_user_service, [backend])

current_user: dict[str, bool] = dict(active=True, verified=True)
super_user: dict[str, bool] = dict(active=True, verified=True, superuser=True)


async def get_jwt_token(request: Request = None) -> str:
    if request:
        if not (token := request.cookies.get(config.auth_cookie_name)):
            if not (token := request.headers.get(config.auth_cookie_name)):
                raise UnauthorizedError

        return token

    raise ValueError("Request must be provided.")


async def parse_jwt_token(
    token: Annotated[str, Depends(get_jwt_token)],
    jwt_strategy: Annotated[JWTStrategy, Depends(get_jwt_strategy)],
    auth_service: Annotated[AuthUserService, Depends(get_auth_user_service)],
) -> User:
    return await jwt_strategy.read_token(token=token, user_manager=auth_service)  # noqa


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
