from json import loads
from pathlib import Path
from uuid import UUID

import pytest
from click import ClickException
from pytest_httpx._httpx_mock import HTTPXMock

from app.models.inputs import InMangaInputs
from app.models.source import Source
from app.providers.inmanga import InMangaProvider

DATA_FILES_PATH = Path(__file__).parent.parent / "data" / "inmanga"
SOURCE = Source(
    provider="InManga",
    inputs=InMangaInputs(
        source_encoded_name="one-punch-man",
        first_chapter_id=UUID("8dcb38ab-2677-4e39-844f-2ac891e607be"),
        source_name="One Punch Man",
        todoist_project_id="",
        todoist_section_id="",
    ),
)
PROCESS_CHAPTER_ID_TEST_CASES = [
    ("1", "1"),
    ("1.0", "1"),
    ("1.1", "1.1"),
    ("1.10", "1.10"),
    ("01", "1"),
    ("01.0", "1"),
    ("001", "1"),
    ("001.00", "1"),
    ("0", "0"),
    ("0.0", "0"),
    ("00", "0"),
]


@pytest.mark.parametrize("chapter_id,expected", PROCESS_CHAPTER_ID_TEST_CASES)
def test_process_chapter_id(chapter_id, expected):
    assert expected == InMangaProvider()._process_chapter_id(chapter_id)


@pytest.mark.asyncio
async def test_inmanga(httpx_mock: HTTPXMock):
    httpx_mock.add_response(content=DATA_FILES_PATH.joinpath("inputs.html").read_bytes())
    result = await InMangaProvider().process_source(source=SOURCE)
    expected = loads(DATA_FILES_PATH.joinpath("results.json").read_text())

    assert len(expected) == len(result)
    for res, exp in zip(result, expected):
        exp["source"] = SOURCE.dict()
        assert exp == res.dict()


@pytest.mark.asyncio
async def test_inmanga_fail(httpx_mock: HTTPXMock):
    httpx_mock.add_response(content=b'{"message": "Forbidden"}', status_code=403)
    with pytest.raises(ClickException, match="Error while fetching .*: 403 .*"):
        await InMangaProvider().process_source(source=SOURCE)
