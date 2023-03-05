from typing import Any
from uuid import UUID

from pydantic import BaseModel, root_validator


class InputsBase(BaseModel):
    source_name: str
    source_encoded_name: str
    todoist_project_id: str
    # TODO: add test for optional todoist_section_id
    todoist_section_id: str | None


class InMangaInputs(InputsBase):
    first_chapter_id: UUID


class TheTVDBInputs(InputsBase):
    pass


class SpyXFamilyInputs(InputsBase):
    source_name: str = "SpyXFamily"
    source_encoded_name: str = "SpyXFamily"

    @root_validator(pre=True)
    def check_forbidden_fields(cls, values: Any) -> Any:
        for field in ("source_name", "source_encoded_name"):
            if field in values:
                raise ValueError(f"{field} cannot be overwritten in SpyXFamilyInputs")
        return values
