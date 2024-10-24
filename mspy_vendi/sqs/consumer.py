# mypy: ignore-errors
# ruff: noqa
import os
import time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mspy_vendi.app.settings")
# Set up Django. We need to do this before importing any DB models.
django.setup()

from mspy_vendi.core.constants import DEFAULT_SOURCE_SYSTEM
from mspy_vendi.core.logger import LOG
from mspy_vendi.core.schemas.nayax import NayaxTransactionSchema
from mspy_vendi.geographies.models import Geography
from mspy_vendi.machines.models import Machine
from mspy_vendi.products.models import Product, ProductCategory
from mspy_vendi.sales.models import Sale
from mspy_vendi.sqs.manager import SQSManager

# Disable logging propagation to prevent Django initial logging setup from interfering with structlog.
LOG.propagate = False


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

        self.consumer = SQSManager(sqs_queue_name, logger=LOG)

    def consume(self):
        """
        Continuously polls an SQS queue for messages and processes them.

        Retrieves and processes messages from the SQS queue, using the specified message handler factory.
        Deletes messages after successful processing or routes them to a Dead Letter Queue if enabled.

        :raise: Exception: Raised if errors occur during message retrieval or processing.
        """
        if not self.is_enabled:
            while True:
                LOG.info(
                    "SQS Consumer is disabled. To enable it set 'NAYAX_CONSUMER_ENABLED' to True. "
                    "Will sleep for 1 hour."
                )

                time.sleep(60 * 60)

        LOG.info(f"Checking SQS '{self.sqs_queue_name}' for messages ...")

        try:
            for message in self.consumer.receive_messages(
                max_number_of_messages=self.sqs_max_number_of_messages,
                wait_time_seconds=self.sqs_long_poll_time,
                visibility_timeout=self.sqs_visibility_timeout,
                auto_ack=self.sqs_auto_ack,  # Enable for PRD environment
            ):
                try:
                    LOG.info(f"Handling message '{message['MessageId']}'.")

                    nayax_item = NayaxTransactionSchema.model_validate_json(message["Body"])

                    geography, is_created = Geography.objects.get_or_create(
                        name=nayax_item.data.area_description or nayax_item.data.actor_description,
                        defaults={"postcode": nayax_item.data.location_code or nayax_item.data.actor_code},
                    )

                    LOG.info("Geography object", geography_name=geography.name, is_created=is_created)

                    machine, is_created = Machine.objects.get_or_create(
                        id=nayax_item.machine_id,
                        defaults={"name": nayax_item.data.machine_name, "geography": geography},
                    )

                    LOG.info("Machine object", machine_id=machine.id, is_created=is_created)

                    for product_item in nayax_item.data.products:
                        LOG.info("Start working with the following product", product_id=product_item.product_id)

                        product_category, is_created = ProductCategory.objects.get_or_create(
                            name=product_item.product_group
                        )

                        LOG.info(
                            "Product category object",
                            product_category_name=product_category.name,
                            is_created=is_created,
                        )

                        LOG.info(
                            "Provided Product object",
                            product_id=product_item.product_id,
                            price=product_item.product_bruto,
                        )

                        product, is_created = Product.objects.get_or_create(
                            id=product_item.product_id,
                            defaults={
                                "name": product_item.product_name,
                                "price": product_item.product_bruto,
                                "category": product_category,
                            },
                        )

                        LOG.info(
                            "Product object",
                            product_id=product.id,
                            is_created=is_created,
                        )

                        LOG.info(
                            "Provided Sale object",
                            sale_id=nayax_item.transaction_id,
                            quantity=product_item.product_quantity,
                            source_system_id=nayax_item.transaction_id,
                        )
                        sale_datetime = nayax_item.machine_time or nayax_item.data.machine_au_time
                        sale, is_created = Sale.objects.get_or_create(
                            id=nayax_item.transaction_id,
                            defaults={
                                "product": product,
                                "machine": machine,
                                "sale_date": sale_datetime.date(),
                                "sale_time": sale_datetime.time(),
                                "quantity": product_item.product_quantity,
                                "source_system": DEFAULT_SOURCE_SYSTEM,
                                "source_system_id": nayax_item.transaction_id,
                            },
                        )

                        LOG.info(
                            "Sale object",
                            sale_id=sale.id,
                            is_created=is_created,
                        )

                    LOG.info(
                        "Message processed successfully.",
                        message_id=message["MessageId"],
                    )

                except Exception as e:
                    LOG.error(f"Error processing message {message['MessageId']}: {e}")

                    if self.sqs_dlq_enabled:
                        # Place the message in the Dead Letter Queue for further analysis
                        continue

        except Exception as e:
            LOG.error(f"Error receiving messages from SQS: {e}", exc_info=True)
