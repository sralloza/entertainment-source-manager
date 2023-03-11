from unittest import mock

from click.testing import CliRunner

from app.cli import cli


@mock.patch("app.cli.main")
def test_main_normal_ok(main_m):
    result = CliRunner().invoke(cli)
    assert result.exit_code == 0

    main_m.assert_called_once_with()


@mock.patch("app.cli.main")
def test_main_update_single_source_ok(main_m):
    result = CliRunner().invoke(cli, ["update-single-source", "test"])
    assert result.exit_code == 0

    main_m.assert_called_once_with("test")


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
