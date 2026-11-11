"""Structured JSON logs on stderr.

A record is written as its timestamp, level, logger, request ID, message and a
fixed allowlist of extra fields. The message must be a fixed event name: callers
pass variable data only through allowlisted fields, so secrets and free text
supplied by a user are never written.
"""

import contextvars
import json
import logging
import sys
import uuid
from datetime import UTC, datetime

request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")

# Extra fields a caller may attach with logger.info("event", extra={...}).
ALLOWED_FIELDS = frozenset({"command", "exit_code", "error_type"})


def new_request_id() -> str:
    value = uuid.uuid4().hex
    request_id.set(value)
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, object] = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "request_id": request_id.get(),
            "event": record.msg if isinstance(record.msg, str) else "invalid_event",
        }
        for key in ALLOWED_FIELDS:
            if key in record.__dict__:
                entry[key] = record.__dict__[key]
        # Exception text is never included, only its type, so a message that
        # carries a secret or user input cannot reach the log.
        if record.exc_info and record.exc_info[0] is not None:
            entry["error_type"] = record.exc_info[0].__name__
        return json.dumps(entry, sort_keys=True)


def configure_logging(level: str) -> logging.Logger:
    logger = logging.getLogger("project_template")
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger
