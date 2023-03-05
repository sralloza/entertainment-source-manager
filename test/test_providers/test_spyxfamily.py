from json import loads
from pathlib import Path

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


@pytest.mark.asyncio
async def test_spyxfamily(httpx_mock: HTTPXMock):
    httpx_mock.add_response(content=DATA_FILES_PATH.joinpath("inputs.html").read_bytes())
    result = await SpyXFamilyProvider().process_source(source=SOURCE)
    expected = loads(DATA_FILES_PATH.joinpath("results.json").read_text())

    assert len(expected) == len(result)
    for res, exp in zip(result, expected):
        exp["source"] = SOURCE.dict()
        assert exp == res.dict()


@pytest.mark.asyncio
async def test_spyxfamily_fail(httpx_mock: HTTPXMock):
    httpx_mock.add_response(content=b'{"message": "Forbidden"}', status_code=403)
    with pytest.raises(ClickException, match="Error while fetching .*: 403 .*"):
        await SpyXFamilyProvider().process_source(source=SOURCE)
