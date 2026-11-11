import json
import logging

import pytest

from project_template.logging_setup import configure_logging, new_request_id

SECRET = "s3cr3t-token-value"  # noqa: S105  # a fake value the tests prove is never logged


def records(capsys: pytest.CaptureFixture[str]) -> list[dict[str, object]]:
    return [json.loads(line) for line in capsys.readouterr().err.splitlines()]


def test_emits_one_json_object_per_line_on_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    request = new_request_id()
    configure_logging("INFO").info("started", extra={"command": "hello"})
    captured = capsys.readouterr()
    assert captured.out == ""
    (entry,) = (json.loads(line) for line in captured.err.splitlines())
    assert entry["event"] == "started"
    assert entry["level"] == "INFO"
    assert entry["request_id"] == request
    assert entry["command"] == "hello"
    assert {"time", "logger"} <= set(entry)


def test_request_ids_differ_per_call() -> None:
    assert new_request_id() != new_request_id()


def test_level_filters_records(capsys: pytest.CaptureFixture[str]) -> None:
    logger = configure_logging("WARNING")
    logger.info("quiet")
    logger.warning("loud")
    assert [entry["event"] for entry in records(capsys)] == ["loud"]


def test_extra_fields_outside_the_allowlist_are_dropped(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging("INFO").info("event", extra={"password": SECRET, "command": "hello"})
    err = capsys.readouterr().err
    assert SECRET not in err
    assert '"command": "hello"' in err


def test_format_arguments_and_free_text_never_reach_the_log(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging("INFO").info("user said %s", SECRET)
    assert SECRET not in capsys.readouterr().err


def test_exception_text_is_not_logged_only_its_type(capsys: pytest.CaptureFixture[str]) -> None:
    logger = configure_logging("INFO")
    try:
        raise ValueError(SECRET)
    except ValueError:
        logger.exception("failed")
    err = capsys.readouterr().err
    assert SECRET not in err
    assert "Traceback" not in err
    assert json.loads(err)["error_type"] == "ValueError"


def test_reconfiguring_does_not_duplicate_handlers() -> None:
    configure_logging("INFO")
    logger = configure_logging("INFO")
    assert len(logger.handlers) == 1
    assert logger.propagate is False
    assert logger.level == logging.INFO
