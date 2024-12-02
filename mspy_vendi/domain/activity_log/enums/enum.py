from enum import StrEnum


class EventTypeEnum(StrEnum):
    USER_REGISTER = "user_register"
    USER_EMAIL_VERIFIED = "user_email_verified"
    USER_FORGOT_PASSWORD = "user_forgot_password"
    USER_RESET_PASSWORD = "user_reset_password"
    USER_DELETED = "user_deleted"
    USER_EDITED = "user_edited"
    USER_SCHEDULE_CREATION = "user_schedule_creation"
    USER_SCHEDULE_DELETION = "user_schedule_deletion"
