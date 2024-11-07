from taskiq import TaskiqMiddleware

from mspy_vendi.core.sentry import setup_sentry


class SentryMiddleware(TaskiqMiddleware):
    def __init__(self, sentry_dsn: str | None = None):
        super().__init__()
        self.sentry_dsn = sentry_dsn

    async def startup(self) -> None:
        setup_sentry(self.sentry_dsn)
