from datetime import datetime

from fastapi_users import schemas
from pydantic import EmailStr, PositiveInt
from pydantic.json_schema import SkipJsonSchema
from pydantic_extra_types.phone_numbers import PhoneNumber

from mspy_vendi.core.constants import MAX_NUMBER_OF_CHARACTERS
from mspy_vendi.core.enums import ExportTypeEnum
from mspy_vendi.core.enums.date_range import ScheduleEnum
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.core.schemas.base import AlphaString, ConstraintString
from mspy_vendi.core.validators import validate_password
from mspy_vendi.domain.machines.schemas import MachineDetailSchema
from mspy_vendi.domain.products.schemas import ProductDetailSchema
from mspy_vendi.domain.user.enums import PermissionEnum, RoleEnum, StatusEnum


class UserBase(BaseSchema):
    firstname: AlphaString
    lastname: AlphaString
    email: EmailStr
    company_name: ConstraintString(MAX_NUMBER_OF_CHARACTERS)
    job_title: ConstraintString(MAX_NUMBER_OF_CHARACTERS)
    phone_number: PhoneNumber | None = None


class UserBaseDetail(UserBase):
    id: PositiveInt
    status: StatusEnum
    role: RoleEnum
    permissions: list[PermissionEnum]
    is_verified: bool
    last_logged_in: datetime | None


class UserAllSchema(UserBaseDetail):
    number_of_machines: int
    number_of_products: int


class UserDetail(UserBaseDetail):
    machines: list[MachineDetailSchema]
    products: list[ProductDetailSchema]


class UserUpdatePerSignIn(BaseSchema):
    last_logged_in: datetime


class UserExistingSchedulesSchema(BaseSchema):
    task_id: str
    export_type: ExportTypeEnum
    schedule: ScheduleEnum
    geography_ids: list[PositiveInt] | None


class UserCreate(UserBase, schemas.BaseUserCreate):
    is_active: SkipJsonSchema[bool | None] = True
    is_superuser: SkipJsonSchema[bool | None] = False
    is_verified: SkipJsonSchema[bool | None] = False

    validate_password = validate_password(field_name="password")


class UserUpdate(BaseSchema):
    firstname: AlphaString | None = None
    lastname: AlphaString | None = None
    company_name: ConstraintString(MAX_NUMBER_OF_CHARACTERS)
    job_title: ConstraintString(MAX_NUMBER_OF_CHARACTERS)
    phone_number: PhoneNumber | None = None


class UserPasswordChange(BaseSchema):
    current_password: str
    new_password: str

    validate_password = validate_password(field_name="new_password")


class UserPasswordUpdate(BaseSchema):
    hashed_password: str


class UserLoginSchema(BaseSchema):
    username: str
    password: str


class UserPermissionsModifySchema(BaseSchema):
    permissions: list[PermissionEnum]


class UserAdminCreateSchema(BaseSchema):
    email: EmailStr
    firstname: AlphaString
    lastname: AlphaString
    permissions: list[PermissionEnum]
    machines: list[PositiveInt]
    products: list[PositiveInt]


class UserAdminEditSchema(BaseSchema):
    firstname: AlphaString | None = None
    lastname: AlphaString | None = None
    permissions: list[PermissionEnum] | None = None
    machines: list[PositiveInt] | None = None
    products: list[PositiveInt] | None = None
    company_logo_image: bytes | None = None


class UserScheduleSchema(BaseSchema):
    """
    Schema for scheduling a user.

    Every field is optional due to backward compatibility.
    If we will add new fields, the existing records will not be affected.
    """

    id: PositiveInt | None = None
    email: EmailStr | None = None
    firstname: AlphaString | None = None
    lastname: AlphaString | None = None
    is_superuser: bool | None = None


class UserCompanyLogoImageSchema(BaseSchema):
    user_id: PositiveInt
    company_logo_image: bytes | None = None
