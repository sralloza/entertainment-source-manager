import re
from json import loads
from pathlib import Path

import pytest
from click import ClickException
from dateutil.parser import parse as parse_date
from pytest_httpx._httpx_mock import HTTPXMock

from app.models.inputs import TheTVDBInputs
from app.models.source import Source
from app.providers.thetvdb import TheTVDBProvider

DATA_FILES_PATH = Path(__file__).parent.parent / "data" / "thetvdb"
params = pytest.mark.parametrize(
    "name,encoded_name",
    [("Sherlock", "sherlock"), ("The Last of Us", "the-last-of-us")],
)
is_ended_map = {
    "Sherlock": True,
    "The Last of Us": False,
}


def get_source(name: str, encoded_name: str):
    return Source(
        provider="TheTVDB",
        inputs=TheTVDBInputs(
            source_encoded_name=encoded_name,
            source_name=name,
            todoist_project_id="",
            todoist_section_id="",
        ),
    )


@pytest.mark.xfail(reason="Fails when called with all tests due to logging to closed stdout")
@pytest.mark.asyncio
@params
async def test_thetvdb(httpx_mock: HTTPXMock, name: str, encoded_name: str, caplog):
    httpx_mock.add_response(
        url=re.compile(f".+/series/{encoded_name}/allseasons/official"),
        content=(DATA_FILES_PATH / f"{encoded_name}/inputs.html").read_bytes(),
    )
    httpx_mock.add_response(
        url=re.compile(f".+/series/{encoded_name}"),
        content=(DATA_FILES_PATH / f"{encoded_name}/info.html").read_bytes(),
    )
    source = get_source(name, encoded_name)
    result = await TheTVDBProvider().process_source(source=source)
    expected = loads(DATA_FILES_PATH.joinpath(f"{encoded_name}/results.json").read_text())
    for elem in expected:
        if elem["released_date"]:
            elem["released_date"] = parse_date(elem["released_date"]).date()

    assert len(expected) == len(result)
    for res, exp in zip(result, expected):
        exp["source"] = source.dict()
        assert exp == res.dict()

    # Series ended log check
    if not is_ended_map[name]:
        assert len(caplog.records) == 0
        return

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == "WARNING"
    assert record.message == f"Series {name!r} has ended"


@pytest.mark.asyncio
@params
async def test_thetvdb_fail_processing(httpx_mock: HTTPXMock, name: str, encoded_name: str):
    httpx_mock.add_response(content=b"<html></html>", status_code=200)
    with pytest.raises(ClickException, match="Could not find series basic info"):
        await TheTVDBProvider().process_source(source=get_source(name, encoded_name))


@pytest.mark.asyncio
@params
async def test_thetvdb_fail_request(httpx_mock: HTTPXMock, name: str, encoded_name: str):
    httpx_mock.add_response(content=b'{"message": "Forbidden"}', status_code=403)
    with pytest.raises(ClickException, match="Error while fetching .*: 403 .*"):
        await TheTVDBProvider().process_source(source=get_source(name, encoded_name))
