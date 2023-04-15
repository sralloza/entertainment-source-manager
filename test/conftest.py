import logging
from typing import Any

import pytest

from app.logs import setup_logging

HANDLER = "_pytest.logging.LogCaptureHandler"


def dict_modifier(dict_config: dict[str, Any]) -> dict[str, Any]:
    dict_config["handlers"]["LogCaptureHandler"] = {
        "class": "_pytest.logging.LogCaptureHandler",
        "level": "DEBUG",
        "filters": [],
        "formatter": "json_formatter",
    }
    logs = dict_config["loggers"].keys()
    for log in logs:
        dict_config["loggers"][log]["handlers"].append("LogCaptureHandler")
    return dict_config


def pytest_configure(config):  # noqa: ARG001
    setup_logging(dict_modifier)


@pytest.fixture(scope="function", autouse=True)
def logging_config(request):
    logging_plugin = request.config.pluginmanager.get_plugin("logging-plugin")
    if handler := logging._handlers.get("LogCaptureHandler"):  # type: ignore[attr-defined]
        logging_plugin.caplog_handler = handler
