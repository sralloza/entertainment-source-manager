from typing import Any

from dateutil.parser import parse
from httpx import Response

from app.models.todoist import Task


def build_task_from_response(response: Response) -> Task:
    json = response.json()
    return _build_task_from_json(json)


def build_tasks_from_response(response: Response) -> list[Task]:
    json = response.json()
    return [_build_task_from_json(task) for task in json]


def _build_task_from_json(json: Any) -> Task:
    try:
        due_date = parse(json["due"]["date"]).date()
    except (KeyError, TypeError):
        due_date = None
    return Task(due_date=due_date, **json)
