import structlog

from core.schemas.nayax import NayaxTransactionSchema
from sqs.manager import SQSManager


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
        logger: structlog.BoundLogger,
    ):
        """
        Initializes the SQSConsumer instance.

        :param sqs_queue_name: str: The name of the SQS queue for message consumption.
        :param handler_factory: Type[SQSMessageHandlerFactory]: Factory class for creating message handlers.
        :param sqs_max_number_of_messages: int: Maximum number of messages to retrieve per call. Defaults to 10.
        :param sqs_visibility_timeout: int: Duration in seconds messages are hidden from queue. Defaults to 30.
        :param sqs_long_poll_time: int: Wait time in seconds for messages if queue is empty. Defaults to 5.
        :param sqs_dlq_enabled: bool: If True, enables Dead Letter Queue handling. Defaults to False.
        :param logger: structlog.BoundLogger: Logger instance for logging. Defaults to structlog.get_logger().
        """

        self.sqs_queue_name = sqs_queue_name
        self.sqs_max_number_of_messages = sqs_max_number_of_messages
        self.sqs_visibility_timeout = sqs_visibility_timeout
        self.sqs_long_poll_time = sqs_long_poll_time
        self.sqs_dlq_enabled = sqs_dlq_enabled
        self.sqs_auto_ack = sqs_auto_ack
        self.logger = logger

        self.consumer = SQSManager(sqs_queue_name, logger=logger)

    def consume(self):
        """
        Continuously polls an SQS queue for messages and processes them.

        Retrieves and processes messages from the SQS queue, using the specified message handler factory.
        Deletes messages after successful processing or routes them to a Dead Letter Queue if enabled.

        :raise: Exception: Raised if errors occur during message retrieval or processing.
        """

        self.logger.info(f"Checking SQS '{self.sqs_queue_name}' for messages ...")

        total_count: int = 0
        success_count: int = 0
        error_count: int = 0

        try:
            for message in self.consumer.receive_messages(
                max_number_of_messages=self.sqs_max_number_of_messages,
                wait_time_seconds=self.sqs_long_poll_time,
                visibility_timeout=self.sqs_visibility_timeout,
                auto_ack=self.sqs_auto_ack,  # Enable for PRD environment
            ):
                total_count += 1

                try:
                    result = NayaxTransactionSchema.model_validate_json(message["Body"])
                    success_count += 1

                    self.logger.info(f"Handling message '{message['MessageId']}'.")

                except Exception as e:
                    self.logger.error(f"Error processing message {message['MessageId']}: {e}")

                    error_count += 1

                    # if self.sqs_dlq_enabled:
                    #     # Place the message in the Dead Letter Queue for further analysis
                    #     continue

                self.logger.info(
                    "Current message processing statistics "
                    f"total_count={total_count}, success_count={success_count}, error_count={error_count}"
                )
        except Exception as e:
            self.logger.error(f"Error receiving messages from SQS: {e}", exc_info=True)
