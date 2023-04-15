import json
from json import loads
from pathlib import Path
from typing import Any

import pytest
from click import ClickException
from pytest_httpx._httpx_mock import HTTPXMock

from app.models.inputs import SpyXFamilyInputs
from app.models.source import Source
from app.providers.spyxfamily import SpyXFamilyProvider

DATA_FILES_PATH = Path(__file__).parent.parent / "data" / "spyxfamily"
SOURCE = Source(
    provider="SpyXFamily",
    inputs=SpyXFamilyInputs(
        todoist_project_id="",
        todoist_section_id="",
    ),
)


class HashableDict(dict):
    def __hash__(self):
        return hash(json.dumps(self, sort_keys=True))

    @classmethod
    def from_dict(cls, d: dict[Any, Any]):
        return cls(**d)

    @classmethod
    def from_list_dict(cls, obj: list[dict[Any, Any]]):
        return [cls.from_dict(d) for d in obj]


@pytest.mark.asyncio
async def test_spyxfamily(httpx_mock: HTTPXMock):
    httpx_mock.add_response(content=DATA_FILES_PATH.joinpath("inputs.html").read_bytes())
    result = await SpyXFamilyProvider().process_source(source=SOURCE)
    expected = loads(DATA_FILES_PATH.joinpath("results.json").read_text())
    expected = [dict(source=SOURCE.dict(), **x) for x in expected]

    expected_set = set(HashableDict.from_list_dict(expected))
    result_set = set(HashableDict.from_list_dict([x.dict() for x in result]))
    assert expected_set == result_set


@pytest.mark.asyncio
async def test_spyxfamily_fail(httpx_mock: HTTPXMock):
    httpx_mock.add_response(content=b'{"message": "Forbidden"}', status_code=403)
    with pytest.raises(ClickException, match="Error while fetching .*: 403 .*"):
        await SpyXFamilyProvider().process_source(source=SOURCE)
import icecream
icecream.install()
icecream.ic.configureOutput(includeContext=True)
