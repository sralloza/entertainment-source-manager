from datetime import date
from json import loads
from pathlib import Path
from unittest import mock

import pytest
from freezegun import freeze_time

from app.core.scheduled import process_scheduled_episodes
from app.models.episodes import ScheduledEpisode
from app.models.todoist import Task, TaskCreate, TaskUpdate

TASKS_FILE = Path(__file__).parent.parent / "data" / "core" / "scheduled_tasks.json"
TASK_LIST = [Task(**x) for x in loads(TASKS_FILE.read_text())]

EPISODES_FILE = Path(__file__).parent.parent / "data" / "core" / "scheduled_episodes.json"
EPISODE_LIST = [ScheduledEpisode(**x) for x in loads(EPISODES_FILE.read_text())]


@pytest.mark.asyncio
@freeze_time("2018-01-01")
@pytest.mark.parametrize("assume_new", [True, False])
@mock.patch("app.core.scheduled.TodoistRepository")
async def test_process_scheduled_episodes(todoist_repo_mock, assume_new):
    repo_mock = mock.AsyncMock()
    todoist_repo_mock.return_value = repo_mock
    repo_mock.list_tasks.return_value = TASK_LIST

    await process_scheduled_episodes(EPISODE_LIST, assume_new)

    todoist_repo_mock.assert_called_once()
    repo = todoist_repo_mock.return_value
    assert repo.list_tasks.call_count == (3 if assume_new else 2)
    repo.list_tasks.assert_any_call(project_id="project-1")
    repo.list_tasks.assert_any_call(project_id="project-2")

    task_create = TaskCreate(
        content="Source 2 3x01",
        description="Released: 2019-01-01 on nginx",
        project_id="project-2",
        section_id=None,
        due_date=date(2019, 1, 1),
    )
    if assume_new:
        assert repo.create_task.call_count == 2
    else:
        repo.create_task.assert_called_once_with(task_create)

    task_update = TaskUpdate(
        description="Released: 2019-01-07 on nginx",
        due_date=date(2019, 1, 7),
        section_id="section-1",
    )
    repo.update_task.assert_called_once_with("task-2", task_update)
