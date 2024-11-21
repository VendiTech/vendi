from typing import LiteralString, cast, Optional, Any

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, models, exceptions
from fastapi_users.schemas import BaseUserCreate

from mspy_vendi.config import config, log
from mspy_vendi.core.email import EmailService
from mspy_vendi.core.exceptions.base_exception import PydanticLikeError, BadRequestError
from mspy_vendi.core.helpers import get_described_user_info, generate_random_password
from mspy_vendi.core.service import CRUDService, UpdateSchema, Schema
from mspy_vendi.domain.user.enums.enum import FrontendLinkEnum
from mspy_vendi.domain.user.filters import UserFilter
from mspy_vendi.domain.user.managers import UserManager
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.schemas import UserPermissionsModifySchema, UserDetail, UserAdminCreateSchema


# ruff: noqa
class AuthUserService(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = config.secret_key
    verification_token_secret = config.secret_key

    def __init__(self, user_db, email_service: EmailService, password_helper=None):
        self.email_service = email_service
        self.css_style: str = """
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                    }
                    .email-content {
                        background-color: white;
                        margin: 0 auto;
                        max-width: 600px;
                        padding: 20px;
                        border: 1px solid #F6B0B1;
                        border-radius: 35px;
                    }
                    .greeting {
                        font-size: 20px;
                        font-weight: bold;
                        color: #2C3344;
                    }
                    .message {
                        font-size: 16px;
                        line-height: 1.5;
                        margin: 10px 0;
                    }

                    .container-link {
                        display: flex;
                        justify-content: center;
                    }

                    .link {
                        display: inline-block;
                        margin: 2px auto;
                        padding: 17px 25px;
                        background-color: #E9EEF9;
                        color: #0050C8 !important;
                        text-decoration: none;
                        border-radius: 20px;
                    }

                    .link:hover{
                        background-color: #fefefe;
                    }
                    .closing {
                        font-size: 16px;
                        line-height: 1.5;
                    }
                    .closing span {
                        display: block;
                        margin-bottom: 20px;
                    }
                    .im {
                        color: black;
                    }
                </style>
            </head>
        """
        self.message_footer: str = """
            <p class="message" style="flex-direction: column">
                If you have any questions or need assistance, feel free to contact us anytime at contact@vendi-portal.com. We’re here to support you and always available to help!
            </p>
            <p class="closing">
                <span>Thank you, and welcome to Vendi!</span>
                Warm regards,<br>
                Vendi Team
            </p>
        """
        super().__init__(user_db, password_helper)

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
        if await self.user_db.get_by_email(user_create.email):
            raise BadRequestError("Provided User already exists")

        if isinstance(user_create, BaseUserCreate):
            await self.validate_password(user_create.password, user_create)
            user_dict: dict[str, Any] = (
                user_create.create_update_dict() if safe else user_create.create_update_dict_superuser()
            )
            password = user_dict.pop("password")
            user_dict["hashed_password"] = self.password_helper.hash(password)

        else:
            user_dict: dict[str, Any] = user_create.model_dump(exclude={"machines"})
            user_dict["hashed_password"] = self.password_helper.hash(generate_random_password())

        created_user = await UserManager(self.user_db.session).create(user_dict, is_unique=True)  # type: ignore

        await self.request_verify(created_user, request)

        return created_user

    async def on_after_request_verify(self, user: User, token: str, request: Request | None = None) -> None:
        if config.debug:
            return None

        verification_link = f"https://{config.frontend_domain}/{FrontendLinkEnum.EMAIL_VERIFY}/?token={token}"

        html_content: str = f"""
            <!DOCTYPE html>
            <html>
            {self.css_style}
            <body>
                <div class="email-content">
                    <p class="greeting">Hi {user.firstname.capitalize()},</p>
                    <p class="message">
                        Thank you for signing up with Vendi!
                        To complete your registration and explore the fascinating possibilities our platform offers, please confirm your email address by clicking the link below:
                    </p>
                    <div class="container-link">
                        <a class="link" href="{verification_link}">Confirm Email Address</a>
                    </div>
                    {self.message_footer}
                </div>
            </body>
            </html>
        """

        await self.email_service.send_message(
            receivers=[user.email],
            subject="Email Verification for Vendi admin",
            html=html_content,
        )
        log.info("Sent verify email message", info=get_described_user_info(user, request=request))

    async def on_after_forgot_password(self, user: User, token: str, request: Request | None = None) -> None:
        if config.debug:
            return None

        reset_link: str = f"https://{config.frontend_domain}/{FrontendLinkEnum.PASSWORD_RESET}/?token={token}"

        html_content: str = f"""
            <!DOCTYPE html>
            <html>
            {self.css_style}
            <body>
                <div class="email-content">
                    <p class="greeting">Hi {user.firstname.capitalize()},</p>
                    <p class="message">
                        We’ve received a request to reset the password for your account. If you didn’t request this, please disregard this email.
                        To reset your password, simply click the link below:
                    </p>
                    <div class="container-link">
                        <a class="link" href="{reset_link}">Reset Password</a>
                    </div>
                    {self.message_footer}
                </div>
            </body>
            </html>
        """

        await self.email_service.send_message(
            receivers=[user.email],
            subject="Reset Your Password",
            html=html_content,
        )
        log.info("Sent forgot password email message", info=get_described_user_info(user, request=request))

    async def on_after_reset_password(self, user: User, request: Request | None = None) -> None:
        if config.debug:
            return None

        sign_in_link: str = f"https://{config.frontend_domain}/{FrontendLinkEnum.LOG_IN}"

        html_content: str = f"""
            <!DOCTYPE html>
            <html>
            {self.css_style}
            <body>
                <div class="email-content">
                    <p class="greeting">Hi {user.firstname.capitalize()},</p>
                    <p class="message">
                        Your password has been successfully reset. You can now log in to Vendi Platform using your new password.
                        To log in again, please click the link below:
                    </p>
                    <div class="container-link">
                        <a class="link" href="{sign_in_link}">Login Link</a>
                    </div>
                    {self.message_footer}
                </div>
            </body>
            </html>
        """

        await self.email_service.send_message(
            receivers=[user.email],
            subject="Password Successfully Reset",
            html=html_content,
        )
        log.info("Sent reset password email message", info=get_described_user_info(user, request=request))

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

    async def update(
        self, obj_id: int, obj: UpdateSchema, *, autocommit: bool = True, raise_error: bool = True, **kwargs: Any
    ) -> UserDetail:
        return await self.manager.update(
            obj_id=obj_id, obj=obj, autocommit=autocommit, raise_error=raise_error, **kwargs
        )

    async def add_permission(self, user_id: int, obj: UserPermissionsModifySchema) -> UserDetail:
        modify_user: User = await self.get(obj_id=user_id)

        return await self.manager.update_permissions(modified_user=modify_user, permissions=obj.permissions)

    async def delete_permissions(self, user_id: int, obj: UserPermissionsModifySchema) -> UserDetail:
        modify_user: User = await self.get(obj_id=user_id)

        return await self.manager.delete_permissions(modified_user=modify_user, permissions=obj.permissions)
