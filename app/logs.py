import logging
import sys
import traceback
from json import dumps

from app.settings import settings
from app.utils.misc import get_version


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = record.getMessage()
        asctime = self.formatTime(record, self.datefmt)
        obj = {
            "timestamp": asctime,
            "level": record.levelname,
            "message": message,
            "version": get_version(),
            "thread": record.threadName,
        }
        if record.exc_info:
            obj["stack_trace"] = self.format_exception()
        return dumps(obj)

    def format_exception(self) -> str:
        lines = traceback.format_exc().splitlines()
        lines = [x for x in lines if "^^^" not in x]
        return "\n".join(lines)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(settings.log_level)

    handler = logging.StreamHandler(sys.stdout)
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
