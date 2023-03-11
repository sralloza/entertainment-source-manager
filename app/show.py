import json
from typing import Any
from uuid import UUID

import click

from app.settings import get_sources


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> str:
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)  # type: ignore[no-any-return] # pragma: no cover


def print_sources() -> None:
    sources = get_sources()
    sources_dict = [x.dict() for x in sources]
    click.echo(json.dumps(sources_dict, indent=2, cls=UUIDEncoder))


def print_source_names() -> None:
    sources = get_sources()
    source_names = [x.inputs.source_name for x in sources]
    click.echo(json.dumps(source_names, indent=2, cls=UUIDEncoder))
