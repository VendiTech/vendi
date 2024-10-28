"""
This module provides a logger class to configure and setup logging using structlog.

The Logger class provides methods to configure logging, including setting the log level and choosing between
JSON and Console rendering. It also sets up processors to customize the format of log entries, such as dropping
redundant keys, renaming keys, and adding contextual information.

The setup_logging method returns a structlog BoundLogger object that can be used to log messages in the FastAPI app.

Example usage:

    logger = Logger()
    log: BoundLogger = logger.setup_logging()
    log.info("Starting FastAPI app")
"""

import logging
import sys

import structlog
from structlog.processors import CallsiteParameter
from structlog.stdlib import BoundLogger
from structlog.typing import EventDict, Processor


# Logging setup for FastAPI https://gist.github.com/nymous/f138c7f06062b7c43c060bf03759c29e
class Logger:
    """
    Configure and setup logging with Structlog.

    Args:
        json_logs (bool, optional): Whether to log in JSON format. Defaults to False.
        log_level (str, optional): Minimum log level to display. Defaults to "INFO".
    """

    def __init__(self, json_logs: bool = False, log_level: str = "INFO"):
        self.json_logs = json_logs
        self.log_level = log_level

    @staticmethod
    def _rename_event_key(_, __, event_dict: EventDict) -> EventDict:
        """
        Log entries keep the text message in the `event` field, but Datadog
        uses the `message` field. This processor moves the value from one field to
        the other.
        See https://github.com/hynek/structlog/issues/35#issuecomment-591321744

        Args:
            _ (Any): Unused.
            __ (Any): Unused.
            event_dict (EventDict): Dictionary containing the log entry.

        Returns:
            EventDict: Modified dictionary with the 'event' key renamed to 'message'.
        """

        event_dict["message"] = event_dict.pop("event", "")
        return event_dict

    @staticmethod
    def _drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
        """
        Processor to remove the 'color_message' key from the log entry.

        Args:
            _ (Any): Unused.
            __ (Any): Unused.
            event_dict (EventDict): Dictionary containing the log entry.

        Returns:
            EventDict: Modified dictionary with the 'color_message' key removed.
        """

        event_dict.pop("color_message", None)
        return event_dict

    def _get_processors(self) -> list[Processor]:
        """
        Returns a list of structlog processors based on the specified configuration.

        Returns:
            list[Processor]: List of structlog processors.
        """

        processors: list[Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.stdlib.ExtraAdder(),
            self._drop_color_message_key,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.CallsiteParameterAdder(
                [
                    CallsiteParameter.FILENAME,
                    CallsiteParameter.FUNC_NAME,
                    CallsiteParameter.LINENO,
                ],
            ),
        ]

        if self.json_logs:
            # We rename the `event` key to `message` only in JSON logs, as Datadog looks for the
            # `message` key but the pretty ConsoleRenderer looks for `event`
            processors.append(self._rename_event_key)
            # Format the exception only for JSON logs, as we want to pretty-print them when
            # using the ConsoleRenderer
            processors.append(structlog.processors.format_exc_info)

        return processors

    @staticmethod
    def _clear_uvicorn_loggers():
        """
        Clears the log handlers for uvicorn loggers, and enables propagation so the messages are caught by our root
        logger and formatted correctly by structlog.
        """

        for _log in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
            # Clear the log handlers for uvicorn loggers, and enable propagation so the messages
            # are caught by our root logger and formatted correctly by structlog
            logging.getLogger(_log).handlers.clear()
            logging.getLogger(_log).propagate = True

    @staticmethod
    def _configure_structlog(processors: list[Processor]):
        """
        Configures structlog with the specified processors and logger factory. Also caches the logger on first use.

        Args:
            processors: The processors to use for structlog.
        """

        structlog.configure(
            processors=processors
            + [
                # Prepare event dict for `ProcessorFormatter`.
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def _configure_logging(self, processors: list[Processor]) -> logging.Logger:
        """
        Configures logging with the specified processors and logging level.

        Args:
            processors: The processors to use for logging.
        Returns:
            Logger: The configured root logger.
        """
        formatter = structlog.stdlib.ProcessorFormatter(
            # These run ONLY on `logging` entries that do NOT originate within structlog.
            foreign_pre_chain=processors,
            # These run on ALL entries after the pre_chain is done.
            processors=[
                # Remove _record & _from_structlog.
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer() if self.json_logs else structlog.dev.ConsoleRenderer(colors=False),
            ],
        )

        handler = logging.StreamHandler()
        # Use OUR `ProcessorFormatter` to format all `logging` entries.
        handler.setFormatter(formatter)
        root_logger = logging.getLogger()

        if hasattr(root_logger, "addHandler"):
            root_logger.addHandler(handler)

        root_logger.setLevel(self.log_level.upper())

        return root_logger

    def _configure(self):
        """
        Configures logging and structlog and log handled exceptions.
        """

        shared_processors: list[Processor] = self._get_processors()
        self._configure_structlog(shared_processors)
        root_logger = self._configure_logging(shared_processors)

        def handle_exception(exc_type, exc_value, exc_traceback):
            """
            Log any uncaught exception instead of letting it be printed by Python
            (but leave KeyboardInterrupt untouched to allow users to Ctrl+C to stop)
            See https://stackoverflow.com/a/16993115/3641865
            """
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            root_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

        sys.excepthook = handle_exception

    def setup_logging(self) -> BoundLogger:
        """
        Set up logging configuration for the application.

        Returns:
            BoundLogger: The configured logger instance.
        """

        self._configure()
        return structlog.get_logger()
