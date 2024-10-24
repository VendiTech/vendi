from django.conf import settings

from core.logger import LOG
from sqs.consumer import SQSConsumer

if __name__ == "__main__":
    SQSConsumer(
        sqs_queue_name=settings.SQS_QUEUE_NAME,
        sqs_max_number_of_messages=settings.SQS_MAX_NUMBER_OF_MESSAGES,
        sqs_visibility_timeout=settings.SQS_VISIBILITY_TIMEOUT,
        sqs_long_poll_time=settings.SQS_LONG_POLL_TIME,
        sqs_auto_ack=settings.SQS_AUTO_ACK,
        logger=LOG,
    ).consume()
