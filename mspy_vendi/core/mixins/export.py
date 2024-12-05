import io
from typing import Any

import pandas as pd
from asyncpg.protocol import Protocol
from starlette.responses import StreamingResponse

from mspy_vendi.config import log
from mspy_vendi.core.constants import CSS_STYLE, DEFAULT_EXPORT_TYPES, MESSAGE_FOOTER
from mspy_vendi.core.email import EmailService
from mspy_vendi.core.enums import ExportTypeEnum
from mspy_vendi.core.enums.date_range import ScheduleEnum
from mspy_vendi.core.enums.export import ExportEntityTypeEnum
from mspy_vendi.core.factory import DataExportFactory
from mspy_vendi.core.filter import BaseFilter
from mspy_vendi.core.pagination import Page
from mspy_vendi.core.schemas import BaseSchema
from mspy_vendi.db.base import Base
from mspy_vendi.domain.user.models import User
from mspy_vendi.domain.user.schemas import UserScheduleSchema


class ExportManager(Protocol):
    async def export(self, query_filter: BaseFilter, user: Base, **kwargs: Any) -> Any: ...


class ExportProtocol(Protocol):
    email_service: EmailService
    manager: ExportManager


class ExportMixin(ExportProtocol):
    async def send_report(
        self,
        query_filter: BaseFilter,
        content: io.BytesIO,
        file_name: str,
        user: UserScheduleSchema,
        schedule: ScheduleEnum,
        *,
        entity: ExportEntityTypeEnum,
    ) -> None:
        """
        Send the entity report to the user.
        Attach the report to the email and send it to the user.

        :param query_filter: The filter to use for the export.
        :param content: The content of the file to send.
        :param file_name: The name of the file to send.
        :param user: The user to send the report to.
        :param schedule: The schedule type of the report.
        :param entity: The entity to export.
        """
        html_content: str = f"""
            <!DOCTYPE html>
            <html>
            {CSS_STYLE}
            <body>
                <div class="email-content">
                    <p class="message">
                       Your Scheduled report for the provided range:
                       {query_filter.date_from.date()} to {query_filter.date_to.date()} is ready.
                    </p>
                    {MESSAGE_FOOTER}
                </div>
            </body>
            </html>
        """

        await self.email_service.send_message(
            receivers=[user.email],
            subject=f"{schedule} {entity.capitalize()}s report for {user.firstname} {user.lastname}",
            html=html_content,
            files=(file_name, content, None),
        )

        log.info("Sent export message was completed.")

    async def export(
        self,
        query_filter: BaseFilter,
        entity: ExportEntityTypeEnum,
        raw_result: bool = True,
        sync: bool = True,
        export_type: ExportTypeEnum | None = None,
        user: UserScheduleSchema | User | None = None,
        schedule: ScheduleEnum | None = None,
    ) -> StreamingResponse | Page[BaseSchema] | None:
        """
        Export the entity data based on the provided filter and export type.

        There are two ways to export the data, sync and async.
            - sync: The data will be returned as a response.
            - async: The data will be sent to the user's email.

        :param query_filter: The filter to use for the export.
        :param entity: The entity to export.
        :param export_type: The type of export to use.
        :param raw_result: Whether the export is raw result.
        :param sync: Whether to export the data sync or async.
        :param user: The user to send the report to.
        :param schedule: The schedule type of the report.

        :return: The StreamingResponse or None.
        """
        entity_data: list[dict] | Page[BaseSchema] = await self.manager.export(
            query_filter, user, raw_result=raw_result
        )

        if not raw_result:
            return entity_data

        file_extension: str = DEFAULT_EXPORT_TYPES[export_type].get("file_extension")
        file_content_type: str = DEFAULT_EXPORT_TYPES[export_type].get("content_type")

        file_name: str = (
            f"{entity.capitalize()} Report Start-date: {query_filter.date_from.date()}"
            f" End-date: {query_filter.date_to.date()}.{file_extension}"
        )

        df = pd.DataFrame(entity_data)

        content: io.BytesIO = await DataExportFactory.transform(export_type).extract(df)

        if sync:
            return StreamingResponse(
                content=content,
                headers={
                    "Access-Control-Expose-Headers": "Content-Disposition",
                    "Content-Disposition": f"""attachment; filename={file_name}""",
                },
                media_type=file_content_type,
            )

        return await self.send_report(
            query_filter=query_filter,
            content=content,
            file_name=file_name,
            user=user,
            schedule=schedule,
            entity=entity,
        )
