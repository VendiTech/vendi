import sentry_sdk
from sentry_sdk import monitor
from sentry_sdk.integrations.logging import ignore_logger
from taskiq import TaskiqScheduler, ZeroMQBroker
from taskiq.schedule_sources import LabelScheduleSource

from mspy_vendi.config import config, log
from mspy_vendi.core.middlewares.sentry_middleware import SentryMiddleware
from mspy_vendi.domain.datajam.service import DataJamService

broker = ZeroMQBroker()
broker.add_middlewares(SentryMiddleware(config.sentry.datajam_cronjob_dsn))

scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])

ignore_logger(__name__)


@broker.task(schedule=[{"cron": config.crontab_twice_a_day}])
@monitor(monitor_slug=config.sentry.datajam_monitoring_slug)
async def extract_datajam_impressions():
    await log.ainfo("Starting extraction of the DataJam impressions")

    try:
        await DataJamService().process_messages()

    except Exception as exc:
        await log.aerror("An error occurred during extraction of the DataJam impressions")

        sentry_sdk.capture_exception(exc)

    finally:
        await log.ainfo("Extraction of the DataJam impressions has been finished")
