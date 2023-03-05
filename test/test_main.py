from json import loads
from pathlib import Path
from unittest import mock

import pytest
from click import ClickException

from app.main import _main, main
from app.models.episodes import NonScheduledEpisode, ScheduledEpisode
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


@pytest.mark.asyncio
@mock.patch("app.main.get_sources")
@mock.patch("app.main.process_source")
@mock.patch("app.main.process_scheduled_episodes")
@mock.patch("app.main.process_non_scheduled_episodes")
async def test_inner_main(pnse_m, pse_m, ps_m, gs_m):
    gs_m.return_value = get_sources()

    episodes = get_scheduled_episodes() + get_non_scheduled_episodes()
    ps_m.side_effect = lambda x: [k for k in episodes if k.source_name == x.inputs.source_name]

    await _main()
    pse_m.assert_called_once_with(get_scheduled_episodes())
    pnse_m.assert_called_once_with(get_non_scheduled_episodes())


class TestMain:
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.inner_main_sm = mock.patch("app.main._main")
        self.inner_main_m = self.inner_main_sm.start()
        yield
        self.inner_main_sm.stop()

    @pytest.mark.asyncio
    async def test_ok(self, caplog):
        await main()
        self.inner_main_m.assert_called_once_with()
        assert len(caplog.records) == 0

    @pytest.mark.asyncio
    async def test_exception(self, caplog):
        self.inner_main_m.side_effect = Exception("test")
        with pytest.raises(ClickException, match="Internal error: test"):
            await main()

        assert len(caplog.records) == 1
        assert "Internal error" in caplog.text
