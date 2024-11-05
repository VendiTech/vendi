import time

import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger

from mspy_vendi.config import log
from mspy_vendi.db.engine import get_db_session
from mspy_vendi.domain.nayax.schemas import NayaxTransactionSchema
from mspy_vendi.domain.nayax.service import NayaxService
from mspy_vendi.domain.sqs.manager import SQSManager

ignore_logger(__name__)


class SQSConsumer:
    """
    A class to process messages from an SQS queue.

    Attributes:
        sqs_queue_name (str): The name of the SQS queue from which messages are consumed.
        sqs_max_number_of_messages (int): Maximum number of messages to retrieve per call.
        sqs_visibility_timeout (int): Duration (in seconds) messages are hidden from subsequent retrieve calls.
        sqs_long_poll_time (int): Wait time (in seconds) for messages if the queue is empty.
        sqs_dlq_enabled (bool): Flag indicating whether a Dead Letter Queue is enabled.
        logger (structlog.BoundLogger): Logger instance for logging activities.
    """

    def __init__(
        self,
        sqs_queue_name: str,
        *,
        sqs_max_number_of_messages: int = 10,
        sqs_visibility_timeout: int = 30,
        sqs_long_poll_time: int = 5,
        sqs_dlq_enabled: bool = False,
        sqs_auto_ack: bool = False,
        is_enabled: bool = True,
    ):
        """
        Initializes the SQSConsumer instance.

        :param sqs_queue_name: str: The name of the SQS queue for message consumption.
        :param sqs_max_number_of_messages: int: Maximum number of messages to retrieve per call. Defaults to 10.
        :param sqs_visibility_timeout: int: Duration in seconds messages are hidden from queue. Defaults to 30.
        :param sqs_long_poll_time: int: Wait time in seconds for messages if queue is empty. Defaults to 5.
        :param sqs_dlq_enabled: bool: If True, enables Dead Letter Queue handling. Defaults to False.
        :param sqs_auto_ack: bool: If True, deletes messages upon retrieval. Defaults to False.
        :param is_enabled: bool: If True, enables the consumer. Defaults to True.
        :param logger: structlog.BoundLogger: Logger instance for logging. Defaults to structlog.get_logger().
        """

        self.sqs_queue_name = sqs_queue_name
        self.sqs_max_number_of_messages = sqs_max_number_of_messages
        self.sqs_visibility_timeout = sqs_visibility_timeout
        self.sqs_long_poll_time = sqs_long_poll_time
        self.sqs_dlq_enabled = sqs_dlq_enabled
        self.sqs_auto_ack = sqs_auto_ack
        self.is_enabled = is_enabled

        self.consumer = SQSManager(sqs_queue_name, logger=log)

    async def consume(self):
        """
        Continuously polls an SQS queue for messages and processes them.

        Retrieves and processes messages from the SQS queue, using the specified message handler factory.
        Deletes messages after successful processing or routes them to a Dead Letter Queue if enabled.

        :raise: Exception: Raised if errors occur during message retrieval or processing.
        """
        if not self.is_enabled:
            while True:
                log.info(
                    "SQS Consumer is disabled. To enable it set 'NAYAX_CONSUMER_ENABLED' to True. "
                    "Will sleep for 1 hour."
                )

                time.sleep(60 * 60)

        log.info(f"Checking SQS '{self.sqs_queue_name}' for messages ...")

        try:
            for message in self.consumer.receive_messages(
                max_number_of_messages=self.sqs_max_number_of_messages,
                wait_time_seconds=self.sqs_long_poll_time,
                visibility_timeout=self.sqs_visibility_timeout,
                auto_ack=self.sqs_auto_ack,  # Enable for PRD environment
            ):
                try:
                    async with get_db_session() as session:
                        log.info(f"Handling message '{message['MessageId']}'.")

                        nayax_message = NayaxTransactionSchema.model_validate_json(message["Body"])
                        await NayaxService(session).process_message(message=nayax_message)

                        log.info("Message processed successfully.", message_id=message["MessageId"])

                except Exception as exc:
                    log.error(f"Error processing message {message['MessageId']}", exc_info=True)

                    sentry_sdk.capture_exception(exc)

                    if self.sqs_dlq_enabled:
                        # Place the message in the Dead Letter Queue for further analysis
                        continue

        except Exception as exc:
            log.error("Error receiving messages from SQS", exc_info=True)

            sentry_sdk.capture_exception(exc)
