from unittest import mock

from click.testing import CliRunner

from app.cli import cli


@mock.patch("app.cli.main")
def test_main_ok(main_m):
    result = CliRunner().invoke(cli)
    assert result.exit_code == 0

    main_m.assert_called_once_with()
