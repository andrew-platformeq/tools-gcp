"""Validate extension telemetry envelopes before bronze insert."""

from __future__ import annotations

FORBIDDEN_PROPERTY_KEYS = frozenset(
    {
        "subject",
        "from",
        "to",
        "cc",
        "body",
        "filename",
        "mailid",
        "mail_id",
        "attachmentid",
        "attachment_id",
        "content",
        "html",
        "text",
        "message",
        "stack",
        "err",
        "error",
    }
)

REQUIRED_TOP_LEVEL = (
    "event",
    "ts",
    "user_email",
    "identity_source",
    "install_id",
    "session_id",
    "extension_version",
    "chrome_version",
    "platform",
)

MAX_BATCH_SIZE = 500
MAX_EVENT_NAME_LEN = 64
MAX_STRING_LEN = 256


def _check_string(value: object, field: str, *, max_len: int = MAX_STRING_LEN) -> str:
    if not isinstance(value, str):
        msg = f"telemetry event field {field} must be a string"
        raise ValueError(msg)
    text = value.strip()
    if not text:
        msg = f"telemetry event field {field} must not be empty"
        raise ValueError(msg)
    if len(text) > max_len:
        msg = f"telemetry event field {field} exceeds max length"
        raise ValueError(msg)
    return text


def validate_properties(properties: object) -> dict:
    if properties is None:
        return {}
    if not isinstance(properties, dict):
        msg = "telemetry event properties must be an object"
        raise ValueError(msg)

    safe: dict = {}
    for key, value in properties.items():
        if not isinstance(key, str):
            msg = "telemetry property keys must be strings"
            raise ValueError(msg)
        if key.lower() in FORBIDDEN_PROPERTY_KEYS:
            msg = f"telemetry forbidden property key: {key}"
            raise ValueError(msg)
        if value is not None:
            safe[key] = value
    return safe


def validate_event(event: object) -> dict:
    if not isinstance(event, dict):
        msg = "telemetry event must be an object"
        raise ValueError(msg)

    validated: dict = {}
    for field in REQUIRED_TOP_LEVEL:
        validated[field] = _check_string(event.get(field), field)

    if len(validated["event"]) > MAX_EVENT_NAME_LEN:
        msg = "telemetry event name too long"
        raise ValueError(msg)

    validated["properties"] = validate_properties(event.get("properties"))
    return validated


def validate_batch(events: object) -> list[dict]:
    if not isinstance(events, list):
        msg = "telemetry batch events must be an array"
        raise ValueError(msg)
    if not events:
        msg = "telemetry batch must include at least one event"
        raise ValueError(msg)
    if len(events) > MAX_BATCH_SIZE:
        msg = f"telemetry batch exceeds max size ({MAX_BATCH_SIZE})"
        raise ValueError(msg)
    return [validate_event(event) for event in events]
