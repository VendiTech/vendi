from datetime import datetime
from typing import Annotated

import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger
from taskiq import Context, TaskiqDepends

from mspy_vendi.broker import broker
from mspy_vendi.config import log
from mspy_vendi.core.constants import DEFAULT_SCHEDULE_TIMEDELTA
from mspy_vendi.core.enums import ExportTypeEnum
from mspy_vendi.core.enums.date_range import ScheduleEnum
from mspy_vendi.core.enums.export import ExportEntityTypeEnum
from mspy_vendi.domain.sales.filters import GeographyFilter, ScheduleGeographyFilter
from mspy_vendi.domain.sales.service import SaleService
from mspy_vendi.domain.user.schemas import UserScheduleSchema

# Turn off Sentry logging tracking for this module
ignore_logger(__name__)


@broker.task(task_name="export_sale_task")
async def export_sale_task(
    *,
    user: UserScheduleSchema,
    schedule: ScheduleEnum,
    export_type: ExportTypeEnum,
    query_filter: GeographyFilter,
    context: Annotated[Context, TaskiqDepends()],
    sale_service: Annotated[SaleService, TaskiqDepends()],
) -> None:
    """
    TaskIQ task to export sales data.
    We use this task to export sales data based on the provided schedule.

    :param user: UserScheduleSchema
    :param schedule: ScheduleEnum
    :param export_type: ExportTypeEnum
    :param query_filter: GeographyFilter
    :param context: Taskiq Context
    :param sale_service: SaleService
    """
    try:
        current_time: datetime = datetime.now()

        query_filter: ScheduleGeographyFilter = ScheduleGeographyFilter(
            geography_id__in=query_filter.geography_id__in,
            date_from=current_time - DEFAULT_SCHEDULE_TIMEDELTA[schedule],
            date_to=current_time,
        )

        log.info(
            "Start the Sale export task",
            context=context.message.labels,
            export_type=export_type,
            query_filter=query_filter.model_dump_json(),
            schedule=schedule,
            email=user.email,
            user_id=user.id,
        )

        await sale_service.export(
            query_filter=query_filter,
            export_type=export_type,
            user=user,
            schedule=schedule,
            sync=False,
            entity=ExportEntityTypeEnum.SALE,
        )

        log.info(
            "Export task was finished",
            schedule=schedule.value,
            email=user.email,
            user_id=user.id,
        )

    except Exception as err:
        log.error(
            "Export task failed",
            schedule=schedule.value,
            email=user.email,
            user_id=user.id,
            error=str(err),
        )
        sentry_sdk.capture_exception(err)
