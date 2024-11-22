from typing import Annotated

from taskiq import Context, TaskiqDepends

from mspy_vendi.broker import broker, redis_source
from mspy_vendi.config import log
from mspy_vendi.domain.sales.service import SaleService
from mspy_vendi.domain.user.services import UserService


@broker.task
async def export_task(
    *,
    user_id: int,
    context: Annotated[Context, TaskiqDepends()],
    user_service: Annotated[UserService, TaskiqDepends()],
    sale_service: Annotated[SaleService, TaskiqDepends()],
) -> None:
    log.info("Start the export task", user_id=user_id, context=context.message.labels)

    result = await user_service.get(user_id)

    log.info("User data", result=result)


@broker.task
async def remove_task(context: Annotated[Context, TaskiqDepends()]) -> None:
    log.info(f"Hello from my_task! Context: {context.message.task_id}")
    result = await redis_source.get_schedules()

    for task in result:
        log.info(f"Hello from my_task! " f"Task Labels: {task.labels}. ")
