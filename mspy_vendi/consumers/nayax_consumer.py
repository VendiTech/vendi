import asyncio

from mspy_vendi.config import config
from mspy_vendi.core.sentry import setup_sentry
from mspy_vendi.domain.sqs.consumer import SQSConsumer


async def main():
    sqs_consumer = SQSConsumer(
        sqs_queue_name=config.sqs.queue_name,
        sqs_max_number_of_messages=config.sqs.max_number_of_messages,
        sqs_visibility_timeout=config.sqs.visibility_timeout,
        sqs_long_poll_time=config.sqs.long_poll_time,
        sqs_auto_ack=config.sqs.auto_ack,
        is_enabled=config.nayax_consumer_enabled,
    )

    await sqs_consumer.consume()


if __name__ == "__main__":
    setup_sentry(config.sentry.nayax_consumer_dsn)
    asyncio.run(main())
