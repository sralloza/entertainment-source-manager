from json import loads
from pathlib import Path
from unittest import mock

import pytest
from click import ClickException

from app.main import _main, main
from app.models.episodes import NonScheduledEpisode, ScheduledEpisode
from app.models.source import Source
from app.settings import _parse_sources

TEST_DATA_FOLDER = Path(__file__).parent / "data" / "main"


def get_sources():
    file = TEST_DATA_FOLDER / "sources.json"
    return _parse_sources(file.read_text())


def get_scheduled_episodes():
    file = TEST_DATA_FOLDER / "scheduled_episodes.json"
    data = loads(file.read_text())
    return [ScheduledEpisode(**x) for x in data]


def get_non_scheduled_episodes():
    file = TEST_DATA_FOLDER / "non_scheduled_episodes.json"
    data = loads(file.read_text())
    return [NonScheduledEpisode(**x) for x in data]


class TestInnerMain:
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.settings_sm = mock.patch("app.main.settings")
        self.gs_sm = mock.patch("app.main.get_sources")
        self.ps_sm = mock.patch("app.main.process_source")
        self.pse_sm = mock.patch("app.main.process_scheduled_episodes")
        self.pnse_sm = mock.patch("app.main.process_non_scheduled_episodes")

        self.settings_m = self.settings_sm.start()
        self.gs_m = self.gs_sm.start()
        self.ps_m = self.ps_sm.start()
        self.pse_m = self.pse_sm.start()
        self.pnse_m = self.pnse_sm.start()

        self.gs_m.return_value = get_sources()

        yield

        self.settings_sm.stop()
        self.gs_sm.stop()
        self.ps_sm.stop()
        self.pse_sm.stop()
        self.pnse_sm.stop()

    @pytest.mark.parametrize("disabled_sources", ["Source 1,Source 3", list()])
    @pytest.mark.parametrize("entire_source", ["Source 1", None])
    @pytest.mark.parametrize("dry_run", [True, False])
    @pytest.mark.asyncio
    async def test_inner_main(self, entire_source, disabled_sources, dry_run):
        real_disabled_sources = ["Source 1", "Source 3"]
        self.settings_m.disabled_sources = disabled_sources

        scheduled_episodes = get_scheduled_episodes()
        non_scheduled_episodes = get_non_scheduled_episodes()
        episodes = scheduled_episodes + non_scheduled_episodes
        self.ps_m.side_effect = lambda x: [
            k for k in episodes if k.source_name == x.inputs.source_name
        ]

        await _main(entire_source, dry_run)

        if entire_source:
            exp_scheduled_episodes = [
                x for x in scheduled_episodes if x.source_name == entire_source
            ]
            exp_non_scheduled_episodes = [
                x for x in non_scheduled_episodes if x.source_name == entire_source
            ]
        elif disabled_sources:
            exp_scheduled_episodes = [
                x for x in scheduled_episodes if x.source_name not in real_disabled_sources
            ]
            exp_non_scheduled_episodes = [
                x for x in non_scheduled_episodes if x.source_name not in real_disabled_sources
            ]
        else:
            exp_scheduled_episodes = scheduled_episodes
            exp_non_scheduled_episodes = non_scheduled_episodes

        assume_new = entire_source is not None
        self.pse_m.assert_called_once_with(
            exp_scheduled_episodes, assume_new=assume_new, dry_run=dry_run
        )
        self.pnse_m.assert_called_once_with(
            exp_non_scheduled_episodes, assume_new=assume_new, dry_run=dry_run
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dry_run", [True, False])
    async def test_error_getting_episodes_from_source(self, caplog, dry_run):
        def process_source(source: Source):
            source_name = source.inputs.source_name
            if source_name == "Source 0":
                raise Exception("Error")
            return [k for k in episodes if k.source_name == source_name]

        scheduled_episodes = get_scheduled_episodes()
        non_scheduled_episodes = get_non_scheduled_episodes()
        episodes = scheduled_episodes + non_scheduled_episodes
        self.ps_m.side_effect = process_source

        await _main(None, dry_run)

        exp_scheduled_episodes = [x for x in scheduled_episodes if x.source_name != "Source 0"]
        self.pse_m.assert_called_once_with(
            exp_scheduled_episodes, assume_new=False, dry_run=dry_run
        )
        self.pnse_m.assert_called_once_with(
            non_scheduled_episodes, assume_new=False, dry_run=dry_run
        )

        log_records = [x for x in caplog.records if x.levelname == "ERROR"]
        assert len(log_records) == 1
        log_record = log_records[0]
        assert log_record.exc_info[0] == Exception
        log_message = log_record.msg % log_record.args
        assert log_message == "Error while processing source 'Source 0'"

    @pytest.mark.asyncio
    async def test_invalid_entire_source(self):
        err = (
            "Invalid source name: 'invalid'. Valid names are: "
            "'Source 0', 'Source 1', 'SpyXFamily', 'Source 3'"
        )
        with pytest.raises(ClickException, match=err):
            await _main("invalid", False)


class TestMain:
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.inner_main_sm = mock.patch("app.main._main")
        self.sl_sm = mock.patch("app.main.setup_logging")
        self.inner_main_m = self.inner_main_sm.start()
        self.sl_m = self.sl_sm.start()
        yield
        self.inner_main_sm.stop()

    @pytest.mark.asyncio
    async def test_without_entire_source(self, caplog):
        await main()
        self.inner_main_m.assert_called_once_with(None, False)
        assert len(caplog.records) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("dry_run", [True, False])
    async def test_with_entire_source(self, caplog, dry_run):
        await main(entire_source="Source 1", dry_run=dry_run)
        self.inner_main_m.assert_called_once_with("Source 1", dry_run)
        assert len(caplog.records) == 0

    @pytest.mark.asyncio
    async def test_exception(self, caplog):
        self.inner_main_m.side_effect = Exception("test")
        with pytest.raises(ClickException, match="Internal error: test"):
            await main()

        assert len(caplog.records) == 1
        log_record = caplog.records[0]
        assert log_record.exc_info[0] == Exception
        assert log_record.exc_info[1] == self.inner_main_m.side_effect
        assert log_record.message == "Internal error"

    @pytest.mark.asyncio
    async def test_click_exception(self, caplog):
        self.inner_main_m.side_effect = ClickException("this is the original error")
        with pytest.raises(ClickException, match="this is the original error"):
            await main()

        assert len(caplog.records) == 0
