from redis.asyncio import ConnectionPool
from taskiq import TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq_redis import ListQueueBroker, RedisScheduleSource

from mspy_vendi.config import config

broker = ListQueueBroker(config.redis.url, queue_name=config.redis.schedule_queue_name)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    state.redis = ConnectionPool.from_url(config.redis.url)


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    await state.redis.disconnect()


# Here's the source that is used to store scheduled tasks
redis_source = RedisScheduleSource(config.redis.url)

# And here's the scheduler that is used to query scheduled sources
scheduler = TaskiqScheduler(broker, sources=[redis_source])
