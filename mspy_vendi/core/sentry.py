import sentry_sdk

from mspy_vendi.config import config
from mspy_vendi.core.enums import AppEnvEnum


def setup_sentry(sentry_dsn: str | None = None) -> None:
    """
    Function to set up sentry in each BE project. We're passing sentry_dsn as an argument since we also want to setup
    sentry for our consumers and other entities which are being set up from the same repository, but with different
    sentry projects.

    :param sentry_dsn: String representing sentry DSN otherwise it will be taken from environment variables.
    """
    if config.environment not in [AppEnvEnum.LOCAL, AppEnvEnum.TEST]:
        sentry_sdk.init(
            dsn=sentry_dsn or config.sentry.dsn,
            traces_sample_rate=config.sentry.traces_sample_rate,
            profiles_sample_rate=config.sentry.profiles_sample_rate,
            enable_tracing=config.sentry.enable_tracing,
            environment=config.environment,
        )
