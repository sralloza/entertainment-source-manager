from app.builders.todoist import build_task_from_response, build_tasks_from_response
from app.core.common import BaseRepository
from app.models.todoist import Task, TaskCreate, TaskUpdate
from app.settings import settings


class TodoistRepository(BaseRepository):
    def __init__(self) -> None:
        super().__init__(
            api_base_url="https://api.todoist.com", bearer_token=settings.todoist_api_key
        )

    async def create_task(self, task_create: TaskCreate) -> Task:
        payload = self._normalize_payload(task_create.dict())
        res = await self._send_request("POST", "/rest/v2/tasks", payload)
        return build_task_from_response(res)

    async def list_tasks(self, project_id: str) -> list[Task]:
        params = {"project_id": project_id}
        res = await self._send_request("GET", "/rest/v2/tasks", params=params)
        return build_tasks_from_response(res)

    async def update_task(self, task_id: str | int, task_update: TaskUpdate) -> Task:
        payload = self._normalize_payload(task_update.dict(exclude_unset=True))
        res = await self._send_request("POST", f"/rest/v2/tasks/{task_id}", payload)
        return build_task_from_response(res)
