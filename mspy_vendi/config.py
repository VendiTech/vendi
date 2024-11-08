from functools import lru_cache
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict

from mspy_vendi.core.enums import AppEnvEnum
from mspy_vendi.core.logger import Logger


class BaseSettings(PydanticBaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_file=".env", env_file_encoding="utf-8")


class CORSSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_prefix="CORS_")

    origins: list[str] = ["*"]
    headers: list[str] = ["*"]
    methods: list[str] = ["*"]
    allow_credentials: bool = True


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_prefix="DATABASE_")

    host: str = "vendi-db"
    user: str = "vendi-user"
    password: str = "vendi-password"
    port: int = 5432
    name: str = "vendi-db"

    pool_size: int = 60
    max_overflow: int = 20

    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.name}"


class SQSSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_prefix="SQS_")

    default_region: str = "eu-north-1"
    secret_access_key: str = str()
    access_key: str = str()

    queue_name: str = "VendiTech_Nayax_Integration"
    max_number_of_messages: int = 10
    visibility_timeout: int = 60 * 60  # 1 hour
    long_poll_time: int = 20
    auto_ack: bool = False


class WebSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WEB_")

    host: str = "0.0.0.0"
    port: int = Field(8080, alias="PORT")

    log_level: str = "info"
    workers: int = 1
    limit_concurrency: int = 10

    @property
    def listen_address(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def is_reload(self) -> bool:
        return AppEnvEnum.from_env() in [AppEnvEnum.LOCAL, AppEnvEnum.TEST]


class RequestClientSettings(BaseSettings):
    ssl_verify: bool = False
    cert_path: str = ""
    key_path: str = ""

    default_connection_timeout: float = 7.0
    max_connection_timeout: float = 15.0


class MailGunSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_prefix="MAILGUN_")

    api_key: str = str()
    region: Literal["eu", "us"] = "us"
    domain_name: str = str()

    @property
    def url(self) -> str:
        if self.region == "us":
            return f"https://api.mailgun.net/v3/{self.domain_name}/messages"

        return f"https://api.eu.mailgun.net/v3/{self.domain_name}/messages"


class DataJamSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow", env_prefix="DATAJAM_")

    schema: str = "https"
    host: str = "datajamportal.com"
    get_data_url: str = "CustomerAPI/GetData/"

    username: str
    password: str

    device_number_path: str = "temporary_datajam_devices.csv"

    @property
    def url(self) -> str:
        return f"{self.schema}://{self.host}/{self.get_data_url}"


class SentrySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SENTRY_")

    dsn: str = str()
    nayax_consumer_dsn: str = str()

    datajam_cronjob_dsn: str = str()
    datajam_monitoring_slug: str = "datajam-monitoring-slug"

    traces_sample_rate: float = 1.0
    profiles_sample_rate: float = 1.0
    enable_tracing: bool = True

    @property
    def is_enabled(self) -> bool:
        """
        Enable Sentry for all environments except LOCAL and TEST accordingly.
        """
        return AppEnvEnum.from_env() not in [AppEnvEnum.LOCAL, AppEnvEnum.TEST]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="allow")

    db: DBSettings = DBSettings()
    sqs: SQSSettings = SQSSettings()
    web: WebSettings = WebSettings()
    cors: CORSSettings = CORSSettings()
    request_client: RequestClientSettings = RequestClientSettings()
    datajam: DataJamSettings = DataJamSettings()
    sentry: SentrySettings = SentrySettings()
    mailgun: MailGunSettings = MailGunSettings()

    log_level: Literal["INFO", "DEBUG", "WARN", "ERROR"] = "INFO"
    log_json_format: bool = False

    docs_url: str = "/api/swagger"
    base_prefix: str = "/api"
    login_url: str = "/api/auth/login"
    frontend_domain: str = str()

    version: str = "0.1.0"

    prefix_app: str
    secret_key: str

    token_lifetime: int = 3600  # 1 hour in seconds

    nayax_consumer_enabled: bool = True

    @property
    def email_sender(self) -> str:
        return f"no-reply@{self.frontend_domain}"

    @property
    def environment(self) -> AppEnvEnum:
        return AppEnvEnum.from_env()

    @property
    def debug(self) -> bool:
        return self.environment in [AppEnvEnum.LOCAL, AppEnvEnum.TEST]

    @property
    def uvicorn_reload(self) -> bool:
        return self.debug

    @property
    def title(self) -> str:
        return f"Vendi Backend. Environment: {self.environment.upper()}"

    @property
    def auth_cookie_name(self) -> str:
        return f"auth_token_{self.environment.lower()}"

    @property
    def auth_cookie_secure(self) -> bool:
        return self.environment not in [AppEnvEnum.LOCAL, AppEnvEnum.TEST]

    auth_cookie_samesite: Literal["strict", "lax", "none"] = "none"
    auth_cookie_domain: str | None = None

    # crontab_twice_a_day: str = "0 0,12 * * *"  # Every day at 00:00 and 12:00
    crontab_twice_a_day: str = "* * * * *"


class TestSettings(Settings):
    pass


@lru_cache()
def get_settings() -> Settings:
    if AppEnvEnum.from_env() == AppEnvEnum.TEST:
        return TestSettings()

    return Settings()


config: Settings = get_settings()
log = Logger(json_logs=config.log_json_format, log_level=config.log_level).setup_logging()
