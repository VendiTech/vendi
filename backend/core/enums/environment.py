import os
from enum import StrEnum


class AppEnvEnum(StrEnum):
    """
    Enum for app environments
    """

    LOCAL = "local"
    STG = "stg"
    PRD = "prd"
    TEST = "test"

    @classmethod
    def from_env(cls) -> "AppEnvEnum":
        """
        Get the app environment from the "ENV_NAME" environment variable

        :return: AppEnvEnum
        """

        try:
            return AppEnvEnum(os.getenv("ENVIRONMENT", AppEnvEnum.PRD.value).lower())
        except ValueError:
            return AppEnvEnum.PRD
