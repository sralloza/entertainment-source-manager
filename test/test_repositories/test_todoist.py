from datetime import date
from json import loads
from pathlib import Path
from test.test_providers import check_invalid_request_log
from unittest import mock

import pytest
from click import ClickException
from pytest_httpx import HTTPXMock

from app.models.settings import Settings
from app.models.todoist import Task, TaskCreate, TaskUpdate
from app.repositories.todoist import TodoistRepository

TEST_DATA_PATH = Path(__file__).parent.parent / "data" / "todoist"


@pytest.fixture(autouse=True)
def mocks():
    new_settings = Settings(
        aws_access_key_id="aws_access_key_id",
        aws_bucket_name="aws_bucket_name",
        aws_region_name="aws_region_name",
        aws_secret_access_key="aws_secret_access_key",
        telegram_token="telegram_token",
        todoist_api_key="todoist_api_key",
    )
    starter = mock.patch("app.repositories.todoist.settings", new=new_settings)
    starter.start()
    yield
    starter.stop()


@pytest.mark.asyncio
async def test_create_task_ok(httpx_mock: HTTPXMock):
    file = TEST_DATA_PATH / "create_task.json"
    httpx_mock.add_response(
        method="POST",
        url="https://api.todoist.com/rest/v2/tasks",
        match_headers={"Authorization": "Bearer todoist_api_key"},
        status_code=200,
        text=file.read_text(),
    )
    repo = TodoistRepository()
    task_create = TaskCreate(
        content="Buy Milk",
        description="",
        project_id="2203306141",
        due_date=date(2016, 9, 1),
    )
    task = await repo.create_task(task_create)
    expected = Task(id="2995104339", **task_create.dict())
    assert task == expected

    request = httpx_mock.get_request()
    assert request is not None
    expected_payload = task_create.dict()
    expected_payload["due_date"] = str(expected_payload["due_date"])
    assert loads(request.content) == expected_payload


@pytest.mark.asyncio
async def test_create_task_fail(httpx_mock: HTTPXMock, caplog):
    httpx_mock.add_response(400, text='{"error": "Bad Request"}')

    repo = TodoistRepository()
    task_create = TaskCreate(
        content="Buy Milk",
        description="",
        project_id="2203306141",
        due_date=date(2016, 9, 1),
    )
    msg = "Error while fetching .+: 400 .+Bad Request"
    with pytest.raises(ClickException, match=msg):
        await repo.create_task(task_create)
    check_invalid_request_log(caplog)


@pytest.mark.asyncio
async def test_list_tasks_ok(httpx_mock: HTTPXMock):
    file = TEST_DATA_PATH / "list_tasks.json"
    httpx_mock.add_response(
        method="GET",
        url="https://api.todoist.com/rest/v2/tasks?project_id=project_id",
        match_headers={"Authorization": "Bearer todoist_api_key"},
        status_code=200,
        text=file.read_text(),
    )

    repo = TodoistRepository()
    expected = [
        Task(
            id="2995104339",
            content="Buy Milk",
            description="",
            project_id="2203306141",
            section_id="7025",
            due_date=date(2016, 9, 1),
        ),
        Task(
            id="2995104339",
            content="Buy Milk",
            description="",
            project_id="2203306141",
            section_id="7025",
            due_date=None,
        ),
    ]
    tasks = await repo.list_tasks("project_id")
    assert tasks == expected

    request = httpx_mock.get_request()
    assert request is not None
    assert request.content == b""


@pytest.mark.asyncio
async def test_list_tasks_fail(httpx_mock: HTTPXMock, caplog):
    httpx_mock.add_response(400, text='{"error": "Bad Request"}')

    repo = TodoistRepository()
    task_create = TaskCreate(
        content="Buy Milk",
        description="",
        project_id="2203306141",
        due_date=date(2016, 9, 1),
    )
    msg = "Error while fetching .+: 400 .+Bad Request"
    with pytest.raises(ClickException, match=msg):
        await repo.create_task(task_create)
    check_invalid_request_log(caplog)


@pytest.mark.asyncio
async def test_update_task_ok(httpx_mock: HTTPXMock):
    file = TEST_DATA_PATH / "update_task.json"
    httpx_mock.add_response(
        method="POST",
        url="https://api.todoist.com/rest/v2/tasks/task_id",
        match_headers={"Authorization": "Bearer todoist_api_key"},
        status_code=200,
        text=file.read_text(),
    )
    repo = TodoistRepository()
    task_update = TaskUpdate(
        content="Buy Coffee",
        due_date=date(2016, 9, 1),
    )
    task = await repo.update_task("task_id", task_update)
    expected = Task(
        id="2995104339",
        section_id="7025",
        project_id="2203306141",
        description="",
        content="Buy Coffee",
        due_date=date(2016, 9, 1),
    )
    assert task == expected

    request = httpx_mock.get_request()
    assert request is not None
    expected_payload = {"content": "Buy Coffee", "due_date": "2016-09-01"}
    expected_payload["due_date"] = str(expected_payload["due_date"])
    assert loads(request.content) == expected_payload


@pytest.mark.asyncio
async def test_update_task_fail(httpx_mock: HTTPXMock, caplog):
    httpx_mock.add_response(400, text='{"error": "Bad Request"}')

    repo = TodoistRepository()
    task_update = TaskUpdate(
        content="Buy Milk",
        description="",
        project_id="2203306141",
        due_date=date(2016, 9, 1),
    )
    msg = "Error while fetching .+: 400 .+Bad Request"
    with pytest.raises(ClickException, match=msg):
        await repo.update_task("task_id", task_update)
    check_invalid_request_log(caplog)
