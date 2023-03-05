from pydantic import BaseModel

from app.models.inputs import InputsBase


class Source(BaseModel):
    provider: str
    inputs: InputsBase
