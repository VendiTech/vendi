from fastapi import APIRouter, FastAPI

from mspy_vendi.api import healthcheck
from mspy_vendi.api.auth_backend import backend
from mspy_vendi.auth import fastapi_users
from mspy_vendi.core.enums import ApiTagEnum
from mspy_vendi.domain.user.schemas import UserCreate, UserDetail

auth_router = APIRouter(prefix="/auth")
root_router = APIRouter()

# FastAPI-User routers
auth_router.include_router(fastapi_users.get_auth_router(backend), tags=[ApiTagEnum.AUTH_LOGIN])
auth_router.include_router(fastapi_users.get_register_router(UserDetail, UserCreate), tags=[ApiTagEnum.AUTH_RESISTER])
auth_router.include_router(fastapi_users.get_verify_router(UserDetail), tags=[ApiTagEnum.AUTH_VERIFY])
auth_router.include_router(fastapi_users.get_reset_password_router(), tags=[ApiTagEnum.AUTH_RESET_PASSWORD])

root_router.include_router(healthcheck.router)
root_router.include_router(auth_router)


def init_routers(app: FastAPI):
    app.include_router(root_router, prefix="/api")
