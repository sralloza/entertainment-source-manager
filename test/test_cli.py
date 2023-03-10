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
