from datetime import datetime, timedelta
from json import loads
from logging import getLogger

from dateutil.parser import parse

from app.utils.misc import get_version


# It fails when using capsys instead of capfd
def test_log_ok(caplog, capfd):
    logger = getLogger("test")
    logger.info("something")

    assert len(caplog.records) == 1

    record = loads(capfd.readouterr().out)
    assert "timestamp" in record
    timestamp = record["timestamp"]
    timestamp = parse(timestamp)
    assert timestamp - datetime.now() < timedelta(seconds=1)
    assert "logger" in record
    assert "lvl" in record
    assert record["lvl"] == "INFO"
    assert "message" in record
    assert record["message"] == "something"
    assert "version" in record
    assert record["version"] == get_version()
    assert "thread" in record
    assert "stack_trace" not in record


# It fails when using capsys instead of capfd
def test_log_exception(caplog, capfd):
    logger = getLogger("test")

    try:
        raise ValueError("the value error")
    except ValueError:
        logger.exception("something")

    assert len(caplog.records) == 1

    record = loads(capfd.readouterr().out)
    assert "timestamp" in record
    timestamp = record["timestamp"]
    timestamp = parse(timestamp)
    assert timestamp - datetime.now() < timedelta(seconds=1)
    assert "lvl" in record
    assert record["lvl"] == "ERROR"
    assert "logger" in record
    assert "message" in record
    assert record["message"] == "something"
    assert "version" in record
    assert record["version"] == get_version()
    assert "thread" in record
    assert "stack_trace" in record
    assert "^^^" not in record["stack_trace"]
    assert "ValueError" in record["stack_trace"]
    assert "the value error" in record["stack_trace"]
    assert "~~~" not in record["stack_trace"]
    assert record["stack_trace"].count("\n") >= 2
