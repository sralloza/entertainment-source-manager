from unittest import mock

import pytest

from app.models.inputs import InputsBase
from app.models.source import Source
from app.providers import process_source

TEST_DATA = [
    ("InManga", 1, 0, 0, None),
    ("TheTVDB", 0, 1, 0, None),
    ("SpyXFamily", 0, 0, 1, None),
    ("Invalid", 0, 0, 0, ValueError("Invalid provider: Invalid")),
]


@mock.patch("app.providers.spyxfamily_provider")
@mock.patch("app.providers.thetvdb_provider")
@mock.patch("app.providers.inmanga_provider")
@pytest.mark.parametrize(
    "provider, inmanga_calls, thetvdb_calls, spyxfamily_calls, exception", TEST_DATA
)
@pytest.mark.asyncio
async def test_process_source(
    inmanga_prov_mock: mock.MagicMock,
    thetvdb_prov_mock: mock.MagicMock,
    spyxfamily_prov_mock: mock.MagicMock,
    provider: str,
    inmanga_calls: int,
    thetvdb_calls: int,
    spyxfamily_calls: int,
    exception: Exception,
):
    inmanga_prov_mock.process_source = mock.AsyncMock()
    thetvdb_prov_mock.process_source = mock.AsyncMock()
    spyxfamily_prov_mock.process_source = mock.AsyncMock()
    inputs = InputsBase(
        source_name="test",
        source_encoded_name="test",
        todoist_project_id="test",
        todoist_section_id="test",
    )
    source = Source(provider=provider, inputs=inputs)

    if exception:
        with pytest.raises(type(exception), match=exception.args[0]):
            await process_source(source)
    else:
        result = await process_source(source)
        if inmanga_calls:
            assert result == inmanga_prov_mock.process_source.return_value
        elif thetvdb_calls:
            assert result == thetvdb_prov_mock.process_source.return_value
        elif spyxfamily_calls:
            assert result == spyxfamily_prov_mock.process_source.return_value

    assert inmanga_prov_mock.process_source.call_count == inmanga_calls
    assert thetvdb_prov_mock.process_source.call_count == thetvdb_calls
    assert spyxfamily_prov_mock.process_source.call_count == spyxfamily_calls
