from pathlib import Path
from unittest import mock
from uuid import UUID

from app.models.inputs import InMangaInputs, SpyXFamilyInputs, TheTVDBInputs
from app.models.source import Source
from app.show import print_source_names, print_sources

TEST_DATA_PATH = Path(__file__).parent.joinpath("data")


def get_sources():
    thetvdb_inputs = TheTVDBInputs(
        source_name="thetvdb.source_name",
        source_encoded_name="thetvdb.source_encoded_name",
        todoist_project_id="thetvdb.todoist_project_id",
        todoist_section_id="thetvdb.todoist_section_id",
    )
    inmanga_inputs = InMangaInputs(
        source_name="inmanga.source_name",
        source_encoded_name="inmanga.source_encoded_name",
        todoist_project_id="inmanga.todoist_project_id",
        todoist_section_id="inmanga.todoist_section_id",
        first_chapter_id=UUID("618e5ccd-0e44-4f6c-b214-31505918af67"),
    )
    spyxfamily_inputs = SpyXFamilyInputs(
        todoist_project_id="spyxfamily.todoist_project_id",
        todoist_section_id="spyxfamily.todoist_section_id",
    )

    return [
        Source(provider="TheTVDB", inputs=thetvdb_inputs),
        Source(provider="InManga", inputs=inmanga_inputs),
        Source(provider="SpyXFamily", inputs=spyxfamily_inputs),
    ]


@mock.patch("app.show.get_sources")
def test_print_sources(get_sources_mock, capsys):
    get_sources_mock.return_value = get_sources()
    print_sources()
    file = TEST_DATA_PATH / "show" / "sources.json"
    expected = file.read_text()
    captured = capsys.readouterr()

    assert captured.out == expected
    assert captured.err == ""


@mock.patch("app.show.get_sources")
def test_print_source_names(get_sources_mock, capsys):
    get_sources_mock.return_value = get_sources()
    print_source_names()
    file = TEST_DATA_PATH / "show" / "source-names.json"
    expected = file.read_text()
    captured = capsys.readouterr()

    assert captured.out == expected
    assert captured.err == ""
