import logging
from typing import Generator

import boto3


class SQSManager:
    """
    A consumer class for AWS Simple Queue Service (SQS).

    This class provides methods to interact with an AWS SQS queue,
    allowing for queue creation, message retrieval, and deletion.

    Attributes:
        sqs (boto3.client): The boto3 SQS client instance.
        queue_name (str): The name of the SQS queue.
        queue_url (str): The URL of the SQS queue.
        logger (structlog.BoundLogger): The logger instance.
    """

    def __init__(
        self,
        queue_name,
        *,
        create_queue: bool = False,
        logger=logging.getLogger(),
    ):
        """
        Initializes the SQSManager instance.

        Sets up the SQS client and fetches or creates the queue based on the provided parameters.

        :param queue_name: str: The name of the SQS queue to manage.
        :param create_queue: bool: If True, creates the queue if it does not exist. Defaults to False.
        :param logger: The logger instance to use for logging. Defaults to structlog.getLogger().
        """

        self.logger = logger
        # we provide creds for AWS implicitly through the ENV
        self.sqs = boto3.client("sqs")
        self.queue_name = queue_name
        self.queue_url = self.get_queue(create_queue=create_queue)

    def get_queue(self, *, create_queue: bool = False) -> str:
        """
        Retrieves or creates the queue URL based on the provided queue name.
        If 'create_queue' is True and the queue does not exist, it creates a new queue.

        :param create_queue: bool: Flag to create the queue if it does not exist. Defaults to False.

        :return: str: The URL of the retrieved or newly created queue.

        :raise: Exception: Raised if queue retrieval or creation fails.
        """

        try:
            queue_url = self.sqs.get_queue_url(QueueName=self.queue_name)["QueueUrl"]
            self.logger.info(f"Queue {self.queue_name} found with URL: {queue_url}")
            return queue_url
        except self.sqs.exceptions.QueueDoesNotExist:
            self.logger.warning(f"Queue named {self.queue_name} does not exist.")
            if not create_queue:
                raise

            return self.create_queue()

    def create_queue(self) -> str:
        """
        Creates an SQS queue with the specified queue name.

        :return: str: The URL of the newly created queue.

        :raise: Exception: Raised if queue creation fails.
        """

        try:
            queue_url = self.sqs.create_queue(QueueName=self.queue_name)["QueueUrl"]
            self.logger.info(f"Queue {self.queue_name} created with URL: {queue_url}")
            return queue_url
        except self.sqs.exceptions.ClientError as e:
            self.logger.warning(f"Could not create queue: {e}")
            raise

    def receive_messages(
        self,
        max_number_of_messages: int = 10,
        wait_time_seconds: int | None = None,
        visibility_timeout: int | None = None,
        auto_ack: bool = False,
    ) -> Generator[dict, None, None]:
        """
        Retrieves messages from the SQS queue.

        This method yields messages continuously until the queue is empty.
        Optionally, messages can be deleted after retrieval.

        :param max_number_of_messages: The maximum number of messages to retrieve in one call, defaults to 10.
        :param wait_time_seconds: The duration (in seconds) the call will wait for messages if the queue is empty,
                                  defaults to None. This value must be between 0 and 20 seconds.
        :param visibility_timeout: The duration (in seconds) that the received messages are hidden from queue.
        :param auto_ack: A flag to delete messages upon retrieval, defaults to False.

        :yield: The messages received from the queue.

        :raise: Exception: Raised if message retrieval fails.
        """

        while True:
            try:
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    AttributeNames=["All"],
                    MessageAttributeNames=["All"],
                    MaxNumberOfMessages=max_number_of_messages,
                    WaitTimeSeconds=wait_time_seconds,
                    VisibilityTimeout=visibility_timeout,
                )

                for message in response.get("Messages", []):
                    yield message

                    if auto_ack:
                        self.delete_message(message)

            except self.sqs.exceptions.ClientError as e:
                self.logger.warning(f"An error occurred while receiving messages: {e}")
                raise

    def delete_message(self, message: dict) -> bool:
        """
        Deletes a specified message from the SQS queue.

        :param message: dict: The message dictionary containing the 'ReceiptHandle'.

        :return: bool: True if the message was successfully deleted, False otherwise.

        :raise: Exception: Raised if message deletion fails.
        """

        try:
            self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message["ReceiptHandle"])
            self.logger.info(f"Message '{message['MessageId']}' deleted successfully.")
            return True

        except self.sqs.exceptions.ClientError as e:
            self.logger.error(f"Failed to delete message '{message['MessageId']}': {e}")
            return False

    def change_message_visibility(self, message: dict, *, visibility_timeout: int) -> bool:
        """
        Changes the visibility timeout of a specified message in the queue.

        :param message: dict: The message dictionary containing the 'ReceiptHandle'.
        :param visibility_timeout: int: The new visibility timeout in seconds for the message.

        :return: bool: True if the visibility timeout was successfully changed, False otherwise.

        :raise: Exception: Raised if changing the visibility timeout fails.
        """

        try:
            self.sqs.change_message_visibility(
                QueueUrl=self.queue_url,
                ReceiptHandle=message["ReceiptHandle"],
                VisibilityTimeout=visibility_timeout,
            )

            self.logger.info(f"Message '{message['MessageId']}' visibility timeout changed successfully.")
            return True

        except self.sqs.exceptions.ClientError as e:
            self.logger.error(f"Failed to change visibility timeout of message '{message['MessageId']}': {e}")
            return False
