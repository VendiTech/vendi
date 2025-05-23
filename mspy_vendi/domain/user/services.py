from datetime import datetime
from importlib import import_module
from typing import LiteralString, cast, Optional, Any

from fastapi import Request, Response, UploadFile
from fastapi_users import BaseUserManager, IntegerIDMixin, schemas, models
from fastapi_users.schemas import BaseUserCreate

from mspy_vendi.core.constants import DEFAULT_SCHEDULE_MAPPING, MESSAGE_FOOTER, CSS_STYLE
from mspy_vendi.core.enums.date_range import ScheduleEnum
from mspy_vendi.core.enums.export import ExportEntityTypeEnum
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.validators import validate_image_file
from mspy_vendi.domain.activity_log.enums import EventTypeEnum
from mspy_vendi.domain.activity_log.manager import ActivityLogManager
from mspy_vendi.domain.activity_log.schemas import (
    ActivityLogBaseSchema,
    ActivityLogStateSchema,
    ActivityLogStateDetailSchema,
    ActivityLogBasicEventSchema,
    ActivityLogExportSchema,
)
from mspy_vendi.domain.machine_user.service import MachineUserService
from mspy_vendi.domain.product_user.service import ProductUserService

from mspy_vendi.domain.sales.filters import GeographyFilter
from taskiq import ScheduledTask

from mspy_vendi.broker import redis_source
from mspy_vendi.config import config, log
from mspy_vendi.core.email import MailGunService
from mspy_vendi.core.enums import ExportTypeEnum
from mspy_vendi.core.exceptions.base_exception import PydanticLikeError, BadRequestError, ForbiddenError
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
    UserAdminCreateSchema,
    UserAdminEditSchema,
    UserUpdatePerSignIn,
    UserCompanyLogoImageSchema,
)
from mspy_vendi.domain.sales.tasks import export_sale_task


# ruff: noqa
class AuthUserService(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = config.secret_key
    verification_token_secret = config.secret_key

    def __init__(self, user_db, email_service: MailGunService, password_helper=None):
        self.email_service = email_service
        self.machine_user_service = MachineUserService(user_db.session)  # type: ignore
        self.product_user_service = ProductUserService(user_db.session)  # type: ignore
        self.activity_log_manager = ActivityLogManager(user_db.session)  # type: ignore
        self.user_service = UserService(user_db.session)  # type: ignore
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
            user_dict: dict[str, Any] = user_create.model_dump(exclude={"machines", "products"})
            user_dict["hashed_password"] = self.password_helper.hash(generate_random_password())

        created_user = await UserManager(self.user_db.session).create(user_dict, is_unique=True)  # type: ignore

        await self.request_verify(created_user, request)

        return created_user

    async def create_flow(self, user_obj: UserAdminCreateSchema) -> UserDetail:
        created_user = await self.create(user_obj)  # type: ignore
        await self.machine_user_service.update_user_machines(created_user.id, *user_obj.machines)
        await self.product_user_service.update_user_products(created_user.id, *user_obj.products)

        user = await self.user_service.get(created_user.id)

        await self.activity_log_manager.create(
            ActivityLogBaseSchema(
                user_id=created_user.id,
                event_type=EventTypeEnum.USER_REGISTER,
                event_context=ActivityLogStateDetailSchema.model_validate(
                    {
                        "firstname": user.firstname,
                        "lastname": user.lastname,
                        "email": user.email,
                        "permissions": user.permissions,
                        "role": user.role,
                        "machine_names": list(map(lambda item: item.name, user.machines)),
                        "product_names": list(map(lambda item: item.name, user.products)),
                    }
                ),
            )
        )

        return user

    async def edit_flow(
        self, user_id: int, user_obj: UserAdminEditSchema, company_logo_image: UploadFile | None = None
    ) -> UserDetail:
        previous_user_state: User = await self.user_service.get(user_id)
        previous_user_state_schema: ActivityLogStateDetailSchema = ActivityLogStateDetailSchema.model_validate(
            {
                "firstname": previous_user_state.firstname,
                "lastname": previous_user_state.lastname,
                "email": previous_user_state.email,
                "permissions": previous_user_state.permissions,
                "role": previous_user_state.role,
                "machine_names": list(map(lambda item: item.name, previous_user_state.machines)),
                "product_names": list(map(lambda item: item.name, previous_user_state.products)),
            }
        )

        await self.user_service.update(user_id, user_obj, raise_error=False, company_logo_image=company_logo_image)  # type: ignore

        if user_obj.machines is not None:
            await self.machine_user_service.update_user_machines(user_id, *user_obj.machines)
        if user_obj.products is not None:
            await self.product_user_service.update_user_products(user_id, *user_obj.products)

        self.user_db.session.expire_all()  # type: ignore
        user = await self.user_service.get(user_id)

        await self.activity_log_manager.create(
            ActivityLogBaseSchema(
                user_id=user_id,
                event_type=EventTypeEnum.USER_EDITED,
                event_context=ActivityLogStateSchema(
                    previous_state=previous_user_state_schema,
                    current_state={
                        "firstname": user.firstname,
                        "lastname": user.lastname,
                        "email": user.email,
                        "permissions": user.permissions,
                        "role": user.role,
                        "machine_names": list(map(lambda item: item.name, user.machines)),
                        "product_names": list(map(lambda item: item.name, user.products)),
                    },
                ),
            )
        )

        return user

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

    async def on_after_verify(self, user: models.UP, request: Optional[Request] = None) -> None:
        await self.activity_log_manager.create(
            ActivityLogBaseSchema(
                user_id=user.id,
                event_type=EventTypeEnum.USER_EMAIL_VERIFIED,
                event_context=ActivityLogBasicEventSchema.model_validate(
                    {"firstname": user.firstname, "lastname": user.lastname, "email": user.email}
                ),
            )
        )

        if config.debug:
            return None

        html_content: str = f"""
            <!DOCTYPE html>
            <html>
            {CSS_STYLE}
            <body>
                <div class="email-content">
                    <p class="greeting">Hi {user.firstname.capitalize()},</p>
                    <p class="message">
                        Your email has been successfully verified.
                        In order to start using Vendi Platform, you need reset your temporary password.
                        We will send you a link to reset your password.
                    </p>
                    {MESSAGE_FOOTER}
                </div>
            </body>
            </html>
        """

        await self.email_service.send_message(
            receivers=[user.email],
            subject="Email Verification Successfully Completed",
            html=html_content,
        )
        log.info("Sent verify email message", info=get_described_user_info(user, request=request))

        await self.forgot_password(user, request)

    async def on_after_login(
        self,
        user: models.UP,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        """
        Perform an update of the User `last_logged_in` column when sign-in occurs into our system.

        :param user: Current User
        :param request: Request from HTTP context
        :param response: Response from HTTP context
        """
        await self.user_service.update(
            obj_id=user.id,
            obj=UserUpdatePerSignIn(last_logged_in=datetime.now()),
        )

    async def on_after_forgot_password(self, user: User, token: str, request: Request | None = None) -> None:
        await self.activity_log_manager.create(
            ActivityLogBaseSchema(
                user_id=user.id,
                event_type=EventTypeEnum.USER_FORGOT_PASSWORD,
                event_context=ActivityLogBasicEventSchema.model_validate(
                    {"firstname": user.firstname, "lastname": user.lastname, "email": user.email}
                ),
            )
        )

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
        await self.activity_log_manager.create(
            ActivityLogBaseSchema(
                user_id=user.id,
                event_type=EventTypeEnum.USER_RESET_PASSWORD,
                event_context=ActivityLogBasicEventSchema.model_validate(
                    {"firstname": user.firstname, "lastname": user.lastname, "email": user.email}
                ),
            )
        )

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

    async def delete(self, obj_id: int, *, autocommit: bool = True, **kwargs: Any) -> None:
        """
        Deletes an entity from the database.

        :param obj_id: Object ID.
        :param autocommit: If True, commits changes to a database, if False - flushes them.
        :param kwargs: Additional keyword arguments.

        :return: None.
        """
        user: User = await self.get(obj_id=obj_id)

        await ActivityLogManager(self.db_session).create(
            ActivityLogBaseSchema(
                user_id=obj_id,
                event_type=EventTypeEnum.USER_DELETED,
                event_context=ActivityLogBasicEventSchema.model_validate(
                    {"firstname": user.firstname, "lastname": user.lastname, "email": user.email}
                ),
            )
        )
        await super().delete(obj_id=obj_id, autocommit=autocommit, **kwargs)

    async def update(
        self, obj_id: int, obj: UpdateSchema, *, autocommit: bool = True, raise_error: bool = True, **kwargs: Any
    ) -> UserDetail:
        if company_logo_image := kwargs.get("company_logo_image", None):
            company_logo_image_bytes = await validate_image_file(company_logo_image)  # type: ignore
            obj.company_logo_image = company_logo_image_bytes

        await self.manager.update(obj_id=obj_id, obj=obj, autocommit=autocommit, raise_error=raise_error, **kwargs)

        return await self.manager.get(obj_id=obj_id)

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

    async def delete_existing_schedule(self, user: User, entity_type: ExportEntityTypeEnum, schedule_id: str):
        """
        Delete the existing schedule for the user with the provided task_id.
        If the task_id doesn't exist for the user, raise an error.

        :param user: The User to delete the schedule for.
        :param entity_type: The entity type to delete the schedule for.
        :param schedule_id: The task ID to delete.
        """
        existing_schedule_mapping: dict[str, UserExistingSchedulesSchema] = {
            user_task.task_id: user_task
            for user_task in await self.get_existing_schedules(user_id=user.id, entity_type=entity_type)
        }

        if not (schedule := existing_schedule_mapping.get(schedule_id)):
            raise BadRequestError(f"Provided schedule_id={schedule_id} doesn't exist for the user.")

        await ActivityLogManager(self.db_session).create(
            ActivityLogBaseSchema(
                user_id=user.id,
                event_type=EventTypeEnum.USER_SCHEDULE_DELETION,
                event_context=ActivityLogExportSchema.model_validate(
                    {
                        "firstname": user.firstname,
                        "lastname": user.lastname,
                        "email": user.email,
                        "entity_type": entity_type,
                        "schedule": schedule.schedule,
                        "export_type": schedule.export_type,
                    }
                ),
            )
        )
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
        user_event_type: str = f"user_{user.id}_{entity_type}_{export_type}_schedule_{schedule.value}_geography_{','.join(map(str, sorted(set(query_filter.geography_id__in or []))))}"

        if not user.is_verified:
            raise BadRequestError("User didn't verify email yet.")

        if await self.check_task_existence(user_event_type):
            raise BadRequestError("Schedule task already exists")

        if not (
            entity_task := getattr(
                import_module(f"mspy_vendi.domain.{entity_type}s.tasks"), f"export_{entity_type}_task", None
            )
        ):
            log.warning("Task doesn't exist.", entity_type=entity_type)
            raise BadRequestError(f"Task for {entity_type} doesn't exist.")

        await ActivityLogManager(self.db_session).create(
            ActivityLogBaseSchema(
                user_id=user.id,
                event_type=EventTypeEnum.USER_SCHEDULE_CREATION,
                event_context=ActivityLogExportSchema.model_validate(
                    {
                        "firstname": user.firstname,
                        "lastname": user.lastname,
                        "email": user.email,
                        "entity_type": entity_type,
                        "schedule": schedule,
                        "export_type": export_type,
                    }
                ),
            )
        )
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

    async def get_users_images(self) -> Page[UserCompanyLogoImageSchema]:
        return await self.manager.get_users_images()
