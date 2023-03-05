from datetime import date
from json import loads
from pathlib import Path
from unittest import mock

import pytest
from freezegun import freeze_time

from app.core.non_scheduled import process_non_scheduled_episodes
from app.models.episodes import NonScheduledEpisode, S3NonScheduledEpisode
from app.models.todoist import TaskCreate

EPISODES_FILE = Path(__file__).parent.parent / "data" / "core" / "non_scheduled_episodes.json"
EPISODE_LIST = [NonScheduledEpisode(**x) for x in loads(EPISODES_FILE.read_text())]

S3_DATA_FILE = Path(__file__).parent.parent / "data" / "core" / "s3_non_scheduled_episodes.json"
S3_DATA = [
    S3NonScheduledEpisode(source_name=k, chapter_id=c)
    for k, v in loads(S3_DATA_FILE.read_text()).items()
    for c in v
]


@freeze_time("2022-01-01")
class TestProcessNonScheduledEpisodes:
    @pytest.fixture(autouse=True)
    def mocks(self):
        self.tr_sm = mock.patch("app.core.non_scheduled.TodoistRepository")
        self.s3r_sm = mock.patch("app.core.non_scheduled.S3Repository")

        self.todoist_repo_m = self.tr_sm.start()
        self.s3_repo_m = self.s3r_sm.start()

        def get_episodes(source_name: str):
            return [x for x in S3_DATA if x.source_name == source_name]

        self.todoist_repo_m.return_value = mock.AsyncMock()
        self.s3_repo_m.return_value = mock.AsyncMock()
        self.s3_repo_m.return_value.get_episodes.side_effect = get_episodes

        yield

        self.tr_sm.stop()
        self.s3r_sm.stop()

    @pytest.mark.asyncio
    async def test_ok(self):
        await process_non_scheduled_episodes(EPISODE_LIST)

        self.todoist_repo_m.assert_called_once()
        assert self.todoist_repo_m.return_value.list_tasks.call_count == 0

        task_create = TaskCreate(
            content="[Source 3 2](https://source-3.com/chapter-2)",
            description="",
            project_id="project-3",
            section_id="section-3",
            due_date=date(2022, 1, 1),
        )
        self.todoist_repo_m.return_value.create_task.assert_called_once_with(task_create)
        self.todoist_repo_m.return_value.update_task.assert_not_called()
        self.s3_repo_m.return_value.update_episodes.assert_called_once_with("Source 3", ["1", "2"])

    @pytest.mark.asyncio
    async def test_no_new_episodes(self):
        self.s3_repo_m.return_value.get_episodes.return_value = []

        await process_non_scheduled_episodes([])

        self.todoist_repo_m.assert_called_once()
        assert self.todoist_repo_m.return_value.list_tasks.call_count == 0
        self.todoist_repo_m.return_value.create_task.assert_not_called()
        self.todoist_repo_m.return_value.update_task.assert_not_called()
        self.s3_repo_m.return_value.update_episodes.assert_not_called()
