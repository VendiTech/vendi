from fastapi_users import schemas
from pydantic import EmailStr, PositiveInt
from pydantic.json_schema import SkipJsonSchema
from pydantic_extra_types.phone_numbers import PhoneNumber

from mspy_vendi.core.constants import MAX_NUMBER_OF_CHARACTERS
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.core.schemas.base import AlphaString, ConstraintString
from mspy_vendi.core.validators import validate_password
from mspy_vendi.domain.user.enums import PermissionEnum, RoleEnum, StatusEnum


class UserBase(BaseSchema):
    firstname: AlphaString
    lastname: AlphaString
    email: EmailStr
    company_name: ConstraintString(MAX_NUMBER_OF_CHARACTERS)
    job_title: ConstraintString(MAX_NUMBER_OF_CHARACTERS)
    phone_number: PhoneNumber | None = None


class UserDetail(UserBase):
    id: PositiveInt
    status: StatusEnum
    role: RoleEnum
    permissions: list[PermissionEnum]


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
