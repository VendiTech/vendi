from taskiq import TaskiqScheduler, ZeroMQBroker
from taskiq.schedule_sources import LabelScheduleSource

from mspy_vendi.config import config, log
from mspy_vendi.domain.datajam.service import DataJamService

broker = ZeroMQBroker()

scheduler = TaskiqScheduler(broker=broker, sources=[LabelScheduleSource(broker)])


@broker.task(schedule=[{"cron": config.crontab_twice_a_day}])
async def extract_datajam_impressions():
    await log.ainfo("Starting extraction of the DataJam impressions")

    try:
        await DataJamService().process_messages()

    except Exception as exc:
        await log.aerror("An error occurred during extraction of the DataJam impressions", exc_info=str(exc))

    finally:
        await log.ainfo("Extraction of the DataJam impressions has been finished")
