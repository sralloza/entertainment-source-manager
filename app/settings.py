from base64 import b64decode
from json import loads
from logging import _nameToLevel
from os import getenv
from typing import Any

from click import ClickException
from dotenv import load_dotenv
from pydantic import ValidationError

from app.models.inputs import InputsBase
from app.models.settings import Settings
from app.models.source import Source
from app.utils.inputs import INPUTS_MAP

load_dotenv(override=True)


def process_inputs(provider: str, inputs: dict[str, Any]) -> InputsBase:
    try:
        return INPUTS_MAP[provider](**inputs)
    except KeyError:
        raise ClickException(f"Invalid provider: {provider}")
    except ValidationError as e:
        # TODO: show invalid values in the error message
        raise ClickException(f"Invalid inputs for provider {provider}: {e}")


def getenv_required(name: str) -> str:
    value = getenv(name)
    if not value:
        raise ClickException(f"Environment variable {name!r} not set")
    return value


def get_log_level() -> str:
    level = getenv("LOG_LEVEL", "DEBUG")
    parsed_level = level.upper()
    if parsed_level not in _nameToLevel:
        raise ClickException(f"Invalid log level: {level}")
    return level


def get_settings() -> Settings:
    return Settings(
        telegram_token=getenv_required("TELEGRAM_TOKEN"),
        todoist_api_key=getenv_required("TODOIST_API_KEY"),
        aws_access_key_id=getenv_required("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=getenv_required("AWS_SECRET_ACCESS_KEY"),
        aws_bucket_name=getenv_required("AWS_BUCKET_NAME"),
        aws_region_name=getenv_required("AWS_REGION_NAME"),
        log_level=get_log_level(),
    )


def get_sources() -> list[Source]:
    data = getenv_required("SOURCES")
    real_data = b64decode(data).decode("utf-8")
    return _parse_sources(real_data)


def _parse_sources(data: Any) -> list[Source]:
    parsed_data = loads(data)

    output = []
    for source in parsed_data:
        inputs = source["inputs"]
        processed_inputs = process_inputs(source["provider"], inputs)
        source["inputs"] = processed_inputs
        output.append(Source(**source))
    return output


settings = get_settings()
