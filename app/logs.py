import logging
import logging.config
from datetime import datetime
from typing import Any

from pythonjsonlogger import jsonlogger

from app.utils.misc import get_version

logger = logging.getLogger(__name__)
LOG_FMT = "%(timestamp)s %(lvl)s %(logger)s %(message)s %(thread)s %(version)s %(stack_trace)s"


class JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(
        self, log_record: dict[str, Any], record: logging.LogRecord, message_dict: dict[str, Any]
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        if "exc_info" in log_record:
            exc_info = log_record["exc_info"]
            del log_record["stack_info"]
            log_record["stack_trace"] = exc_info

        timestamp = datetime.fromtimestamp(record.created)
        log_record["timestamp"] = timestamp.isoformat(timespec="milliseconds") + "Z"

        log_record["lvl"] = record.levelname.upper()
        log_record["logger"] = record.name
        log_record["thread"] = record.threadName
        log_record["version"] = get_version()

        fields_to_filter = ("message", "stack_trace")
        for field in fields_to_filter:
            if not log_record[field]:
                del log_record[field]


def setup_logging() -> None:
    logging_config: dict[str, Any] = {
        "version": 1,
        "loggers": {
            "": {
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["normal_handler"],
            },
            # TODO: this should be managed by the root logger
            "app": {
                "level": "DEBUG",
                "propagate": False,
                "handlers": ["normal_handler"],
            },
        },
        "handlers": {
            "normal_handler": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "level": "DEBUG",
                "filters": [],
                "formatter": "json_formatter",
            },
        },
        "filters": {},
        "formatters": {
            "json_formatter": {
                "()": JsonFormatter,
                "fmt": LOG_FMT,
            }
        },
    }

    # disabled_loggers = ()
    # for logger in disabled_loggers:
    #     logging_config["loggers"][logger] = {"level": "ERROR", "propagate": False}

    logging.config.dictConfig(logging_config)
