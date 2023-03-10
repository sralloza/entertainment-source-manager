import uuid
from pathlib import Path
from unittest import mock

import pytest
from click import ClickException

from app.models.inputs import InMangaInputs, SpyXFamilyInputs, TheTVDBInputs
from app.models.source import Source
from app.settings import get_log_level, get_settings, get_sources, getenv_required, process_inputs

INPUTS_THETVDB = TheTVDBInputs(
    source_encoded_name="test",
    source_name="test",
    todoist_project_id="test",
    todoist_section_id="test",
)
INPUTS_INMANGA = InMangaInputs(
    first_chapter_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
    source_encoded_name="test",
    source_name="test",
    todoist_project_id="test",
    todoist_section_id="test",
)
SPY_XFAMILY_INPUTS = SpyXFamilyInputs(todoist_project_id="test", todoist_section_id="test")
PROCESS_INPUTS_TEST_DATA = (
    ("TheTVDB", INPUTS_THETVDB),
    ("InManga", INPUTS_INMANGA),
    ("SpyXFamily", SPY_XFAMILY_INPUTS),
)


@pytest.mark.parametrize("provider,expected", PROCESS_INPUTS_TEST_DATA)
def test_process_inputs_ok(provider, expected):
    res = process_inputs(provider, expected.dict(exclude_unset=True))
    assert res == expected


def test_process_inputs_invalid_provider():
    with pytest.raises(ClickException, match="Invalid provider: test"):
        process_inputs("test", {})


def test_process_inputs_invalid_inputs():
    with pytest.raises(ClickException, match="Invalid inputs for provider TheTVDB"):
        process_inputs("TheTVDB", {})


GETENV_REQUIRED_TEST_DATA = (
    ("test", "test", "test"),
    ("test", None, ClickException("Environment variable 'test' not set")),
)


@pytest.mark.parametrize("env_name,env_value,result", GETENV_REQUIRED_TEST_DATA)
@mock.patch("app.settings.getenv")
def test_getenv_required(getenv_mock, env_name, env_value, result):
    getenv_mock.return_value = env_value
    if isinstance(result, Exception):
        with pytest.raises(type(result), match=str(result)):
            getenv_required(env_name)
    else:
        assert getenv_required(env_name) == result


LOG_LEVEL_TEST_DATA = (
    ("CRITICAL", "CRITICAL"),
    ("FATAL", "FATAL"),
    ("ERROR", "ERROR"),
    ("WARN", "WARN"),
    ("WARNING", "WARNING"),
    ("INFO", "INFO"),
    ("DEBUG", "DEBUG"),
    ("NOTSET", "NOTSET"),
    ("whatever", ClickException("Invalid log level: whatever")),
)


@pytest.mark.parametrize("env_value,expected", LOG_LEVEL_TEST_DATA)
@mock.patch("app.settings.getenv")
def test_get_log_level(getenv_mock, env_value, expected):
    getenv_mock.return_value = env_value
    if isinstance(expected, Exception):
        with pytest.raises(type(expected), match=str(expected)):
            get_log_level()
    else:
        assert get_log_level() == expected


@pytest.mark.parametrize("tg_active", (True, False))
@mock.patch("app.settings.getenv")
def test_get_settings_ok(getenv_mock, tg_active):
    def custom_getenv(key: str, default: str | None = None) -> str | None:
        if key == "TELEGRAM_TOKEN" and tg_active is False:
            return None
        elif key == "TELEGRAM_CHAT_ID" and tg_active is False:
            return None
        return default or key

    getenv_mock.side_effect = custom_getenv
    settings = get_settings()
    if tg_active:
        assert settings.telegram_token == "TELEGRAM_TOKEN"
        assert settings.telegram_chat_id == "TELEGRAM_CHAT_ID"
        assert settings.telegram_enabled is True
    else:
        assert settings.telegram_token is None
        assert settings.telegram_chat_id is None
        assert settings.telegram_enabled is False

    assert settings.todoist_api_key == "TODOIST_API_KEY"
    assert settings.aws_access_key_id == "AWS_ACCESS_KEY_ID"
    assert settings.aws_secret_access_key == "AWS_SECRET_ACCESS_KEY"
    assert settings.aws_bucket_name == "AWS_BUCKET_NAME"
    assert settings.aws_region_name == "AWS_REGION_NAME"
    assert settings.log_level == "DEBUG"


@pytest.mark.parametrize("token,chat_id", [("token", None), (None, "chat_id")])
@mock.patch("app.settings.getenv")
def test_get_settings_fail(getenv_mock, token, chat_id):
    env_vars = {"TELEGRAM_TOKEN": token, "TELEGRAM_CHAT_ID": chat_id}

    def getenv_custom(key: str, default: str | None = None) -> str | None:
        if key in env_vars:
            return env_vars[key]
        return default or key

    getenv_mock.side_effect = getenv_custom
    err = "Must set both TELEGRAM_TOKEN and TELEGRAM_CHAT_ID or neither."
    with pytest.raises(ClickException, match=err):
        get_settings()


class TestGetSources:
    @mock.patch("app.settings.getenv")
    def test_sources_not_defined(self, getenv_mock):
        getenv_mock.return_value = None
        with pytest.raises(ClickException, match="Environment variable 'SOURCES' not set"):
            get_sources()

    @mock.patch("app.settings.getenv_required")
    def test_sources_ok(self, getenv_req_mock):
        sources_path = Path(__file__).parent.joinpath("data/sources.txt")
        getenv_req_mock.return_value = sources_path.read_text()
        thetvdb_inputs = TheTVDBInputs(
            source_name="thetvdb.source_name",
            source_encoded_name="thetvdb.source_encoded_name",
            todoist_project_id="thetvdb.todoist_project_id",
            todoist_section_id="thetvdb.todoist_section_id",
        )
        inmanga_inputs = InMangaInputs(
            source_name="inmanga.source_name",
            source_encoded_name="inmanga.source_encoded_name",
            todoist_project_id="inmanga.todoist_project_id",
            todoist_section_id="inmanga.todoist_section_id",
            first_chapter_id=uuid.UUID("618e5ccd-0e44-4f6c-b214-31505918af67"),
        )
        spyxfamily_inputs = SpyXFamilyInputs(
            todoist_project_id="spyxfamily.todoist_project_id",
            todoist_section_id="spyxfamily.todoist_section_id",
        )

        expected = [
            Source(provider="TheTVDB", inputs=thetvdb_inputs),
            Source(provider="InManga", inputs=inmanga_inputs),
            Source(provider="SpyXFamily", inputs=spyxfamily_inputs),
        ]

        assert get_sources() == expected
