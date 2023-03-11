from unittest import mock

import pytest
from click.testing import CliRunner

from app.cli import cli


@mock.patch("app.cli.main")
@pytest.mark.parametrize("dry_run", [True, False])
def test_main_normal_ok(main_m, dry_run):
    args = [] if not dry_run else ["--dry-run"]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0

    main_m.assert_called_once_with(dry_run=dry_run)


@mock.patch("app.cli.main")
@pytest.mark.parametrize("dry_run", [True, False])
def test_main_update_single_source_ok(main_m, dry_run):
    args = [] if not dry_run else ["--dry-run"]
    args += ["update-single-source", "test"]
    result = CliRunner().invoke(cli, args)
    assert result.exit_code == 0

    if dry_run:
        main_m.assert_called_once_with(entire_source="test", dry_run=True)
    else:
        main_m.assert_called_once_with(entire_source="test", dry_run=False)


@mock.patch("app.cli.print_sources")
def test_print_helper_sources(print_sources_m):
    result = CliRunner().invoke(cli, ["print", "sources"])
    assert result.exit_code == 0

    print_sources_m.assert_called_once_with()


@mock.patch("app.cli.print_source_names")
def test_print_helper_source_names(print_source_names_m):
    result = CliRunner().invoke(cli, ["print", "source-names"])
    assert result.exit_code == 0

    print_source_names_m.assert_called_once_with()
