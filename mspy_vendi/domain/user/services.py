from typing import LiteralString, cast, Optional, Any

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, models, exceptions

from mspy_vendi.config import config
from mspy_vendi.core.exceptions.base_exception import PydanticLikeError
from mspy_vendi.core.service import CRUDService
from mspy_vendi.domain.user.filters import UserFilter
from mspy_vendi.domain.user.managers import UserManager
from mspy_vendi.domain.user.models import User


# ruff: noqa
class AuthUserService(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = config.secret_key
    verification_token_secret = config.secret_key

    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UP:
        """
        Create a user in database.

        Triggers the on_after_register handler on success.

        :param user_create: The UserCreate model to create.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the creation, defaults to False.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :raises UserAlreadyExists: A user already exists with the same e-mail.
        :return: A new user.
        """
        await self.validate_password(user_create.password, user_create)

        if await self.user_db.get_by_email(user_create.email):
            raise exceptions.UserAlreadyExists

        user_dict: dict[str, Any] = (
            user_create.create_update_dict() if safe else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)

        return await UserManager(self.user_db.session).create(user_dict, is_unique=True)  # type: ignore

    async def validate_password(self, password: str, user: User) -> None:
        """
        Password validation hook, which is triggered in fastapi-users routes (currently on register & reset_password).
        """
        errors = []

        if not 8 <= len(password) <= 128:
            errors.append("Password should be at least 8 and maximum 128 characters.")
        if not all(char.isascii() or char.isprintable() for char in password):
            errors.append("Password must contain only ASCII or printable Unicode characters.")
        if any(char.isspace() for char in password):
            errors.append("Password must not contain spaces at the beginning or end.")
        if password == user.email:
            errors.append("Password cannot be the same as the email.")

        if errors:
            # Adjust error message to look like Pydantic's
            message = f"[{', '.join(f"'{i}'" for i in errors)}]" if len(errors) > 1 else errors[0]  # type: ignore

            raise PydanticLikeError(
                message=cast(LiteralString, message),
                location=("password",),
                input_=password,
            )


class UserService(CRUDService):
    manager_class = UserManager
    filter_class = UserFilter
