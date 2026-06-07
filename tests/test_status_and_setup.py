from kairo.cli.app import status, setup
from click.testing import CliRunner


def test_status_command_runs():
    runner = CliRunner()
    result = runner.invoke(status, [])
    assert result.exit_code == 0
