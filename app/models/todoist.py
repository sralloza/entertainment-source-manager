from datetime import date

from pydantic import BaseModel


class TaskCreate(BaseModel):
    content: str
    description: str
    project_id: str
    section_id: str | None = None
    due_date: date


class Task(TaskCreate):
    due_date: date | None = None  # type: ignore[assignment]
    id: str


class TaskUpdate(BaseModel):
    content: str | None = None
    description: str | None = None
    project_id: str | None = None
    section_id: str | None = None
    due_date: date | None = None

    def __bool__(self) -> bool:
        return bool(self.dict(exclude_unset=True))
