import json

import pytest
from typer.testing import CliRunner

from project_template import __version__
from project_template.cli import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PT_LOG_LEVEL", raising=False)
    monkeypatch.delenv("PT_MAX_NAME_LENGTH", raising=False)


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_hello_greets_and_logs_json_to_stderr() -> None:
    result = runner.invoke(app, ["hello", "--name", "Ada"])
    assert result.exit_code == 0
    assert result.stdout == "Hello, Ada!\n"
    assert json.loads(result.stderr)["event"] == "hello"


def test_invalid_name_is_a_plain_message_and_exit_1() -> None:
    result = runner.invoke(app, ["hello", "--name", "   "])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "error: name must not be empty" in result.stderr
    assert "Traceback" not in result.stderr


def test_name_over_the_configured_limit_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PT_MAX_NAME_LENGTH", "3")
    result = runner.invoke(app, ["hello", "--name", "Ada Lovelace"])
    assert result.exit_code == 1
    assert "at most 3 characters" in result.stderr


def test_invalid_config_is_a_plain_message_and_exit_1(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PT_LOG_LEVEL", "s3cr3t")
    result = runner.invoke(app, ["hello", "--name", "Ada"])
    assert result.exit_code == 1
    assert "error: invalid configuration: log_level" in result.stderr
    assert "s3cr3t" not in result.stderr
    assert "Traceback" not in result.stderr


def test_missing_name_is_a_usage_error_with_exit_2() -> None:
    assert runner.invoke(app, ["hello"]).exit_code == 2
