from importlib import import_module
from typing import LiteralString, cast, Optional, Any

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, models
from fastapi_users.schemas import BaseUserCreate

from mspy_vendi.core.constants import DEFAULT_SCHEDULE_MAPPING, MESSAGE_FOOTER, CSS_STYLE
from mspy_vendi.core.enums.date_range import ScheduleEnum
from mspy_vendi.core.enums.export import ExportEntityTypeEnum

from mspy_vendi.domain.sales.filter import GeographyFilter
from taskiq import ScheduledTask

from mspy_vendi.broker import redis_source
from mspy_vendi.config import config, log
from mspy_vendi.core.email import MailGunService
from mspy_vendi.core.enums import ExportTypeEnum
from mspy_vendi.core.exceptions.base_exception import PydanticLikeError, BadRequestError
from mspy_vendi.core.helpers import get_described_user_info, generate_random_password
from mspy_vendi.core.service import CRUDService, UpdateSchema
from mspy_vendi.domain.user.enums.enum import FrontendLinkEnum
from mspy_vendi.domain.user.filters import UserFilter
from mspy_vendi.domain.user.managers import UserManager
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.schemas import (
    UserPermissionsModifySchema,
    UserDetail,
    UserScheduleSchema,
    UserExistingSchedulesSchema,
)
from mspy_vendi.domain.sales.tasks import export_sale_task


# ruff: noqa
class AuthUserService(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = config.secret_key
    verification_token_secret = config.secret_key

    def __init__(self, user_db, email_service: MailGunService, password_helper=None):
        self.email_service = email_service
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
            {CSS_STYLE}
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
                    {MESSAGE_FOOTER}
                </div>
            </body>
            </html>
        """

        await self.email_service.send_message(
            receivers=[user.email],
            subject="Email Verification for Vendi application",
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
            {CSS_STYLE}
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
                    {MESSAGE_FOOTER}
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
            {CSS_STYLE}
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
                    {MESSAGE_FOOTER}
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

    @staticmethod
    async def check_task_existence(event_type: str) -> bool:
        """
        Check if the task exists in the task queue.

        :param event_type: The event type to check.

        :return: True if the task exists, False otherwise.
        """
        tasks: list[ScheduledTask] = await redis_source.get_schedules()

        return any(task.labels.get("event_type") == event_type for task in tasks)

    @staticmethod
    async def get_existing_schedules(
        user_id: int, entity_type: ExportEntityTypeEnum
    ) -> list[UserExistingSchedulesSchema]:
        """
        Get the existing schedules for the user.
        Return the schedules that are related to the user.

        :param user_id: The user ID to get the schedules for.
        :param entity_type: The entity type to get the schedules for.

        :return: The list of existing schedules for the user.
        """
        user_tasks: list[ScheduledTask] = [
            task
            for task in await redis_source.get_schedules()
            if task.labels.get("event_type").startswith(f"user_{user_id}_{entity_type}")
        ]

        return [
            UserExistingSchedulesSchema(
                task_id=user_task.schedule_id,
                schedule=user_task.kwargs.get("schedule"),
                export_type=user_task.kwargs.get("export_type"),
                geography_ids=user_task.kwargs.get("query_filter", {}).get("geography_id__in"),
            )
            for user_task in user_tasks
        ]

    async def delete_existing_schedule(self, user_id: int, entity_type: ExportEntityTypeEnum, schedule_id: str):
        """
        Delete the existing schedule for the user with the provided task_id.
        If the task_id doesn't exist for the user, raise an error.

        :param user_id: The user ID to delete the schedule for.
        :param entity_type: The entity type to delete the schedule for.
        :param schedule_id: The task ID to delete.
        """
        if schedule_id not in [
            user_task.task_id
            for user_task in await self.get_existing_schedules(user_id=user_id, entity_type=entity_type)
        ]:
            raise BadRequestError(f"Provided schedule_id={schedule_id} doesn't exist for the user.")

        await redis_source.delete_schedule(schedule_id)

    async def schedule_export(
        self,
        user: User,
        export_type: ExportTypeEnum,
        query_filter: GeographyFilter,
        schedule: ScheduleEnum,
        *,
        entity_type: ExportEntityTypeEnum,
    ) -> None:
        """
        Schedule the export task for the user with provided entity_type attribute.
        Before scheduling the task, we check if the user is verified and if the task already exists.

        :param user: The user to schedule the task for.
        :param export_type: The type of export to schedule.
        :param query_filter: The filter to use for the export.
        :param schedule: The schedule type to use for the export.
        :param entity_type: The entity type to use for the export.
        """
        user_event_type: str = f"user_{user.id}_{entity_type}_{export_type}_schedule_{schedule.value}_geography_{",".join(map(str, sorted(set(query_filter.geography_id__in or []))))}"

        if not user.is_verified:
            raise BadRequestError("User didn't verify email yet.")

        if await self.check_task_existence(user_event_type):
            raise BadRequestError("Schedule task already exists")

        entity_task = getattr(import_module(f"mspy_vendi.domain.{entity_type}s.tasks"), f"export_{entity_type}_task")

        await (
            entity_task.kicker()
            .with_labels(event_type=user_event_type)
            .schedule_by_cron(
                redis_source,
                DEFAULT_SCHEDULE_MAPPING[schedule],
                user=UserScheduleSchema.model_validate(user),
                schedule=schedule,
                export_type=export_type,
                query_filter=query_filter,
            )
        )
