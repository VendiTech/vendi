import io
from typing import Generic, TypeVar

from starlette import status

from mspy_vendi.config import config, log
from mspy_vendi.core.client import RequestClient
from mspy_vendi.core.enums import RequestMethodEnum

Client = TypeVar("Client")


class EmailService(Generic[Client]):
    """
    Service for sending emails.
    """

    def __init__(self, client: Client):
        self.client = client

    async def send_message(
        self,
        receivers: list[str],
        subject: str,
        text: str | None = None,
        html: str | None = None,
        files: tuple | None = None,
    ) -> None:
        raise NotImplementedError


class MailGunService(EmailService[RequestClient]):
    async def send_message(
        self,
        receivers: list[str],
        subject: str,
        text: str | None = None,
        html: str | None = None,
        files: tuple[str, bytes | io.BytesIO, str | None] | None = None,
    ) -> None:
        content_params: dict[str, str | None] = {"html": html} if html else {"text": text}
        files_params: dict[str, tuple[str, bytes | io.BytesIO, str | None]] = {"attachment": files} if files else None

        response = await self.client.send_request(
            method=RequestMethodEnum.POST,
            url=config.mailgun.url,
            auth=("api", config.mailgun.api_key),
            data={
                "from": config.email_sender,
                "to": receivers,
                "subject": subject,
                **content_params,
            },
            files=files_params,
        )

        if response.status_code != status.HTTP_200_OK:
            log.error("Couldn't send the email, reason: ", reason=response.text)
