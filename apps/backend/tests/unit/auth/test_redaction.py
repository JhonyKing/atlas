from atlas.privacy.redaction import redact_mapping, redact_secret


def test_redact_secret_never_returns_secret_value() -> None:
    assert redact_secret("session-token-123") == "[REDACTED]"
    assert "session-token-123" not in redact_secret("session-token-123")


def test_redact_mapping_removes_nested_sensitive_fields() -> None:
    event = {
        "request_id": "req-1",
        "subject_id": "user-1",
        "authorization": "Bearer secret",
        "nested": {"private_content": "do not emit", "status": "clean"},
    }

    redacted = redact_mapping(event)

    assert redacted == {
        "request_id": "req-1",
        "subject_id": "user-1",
        "authorization": "[REDACTED]",
        "nested": {"private_content": "[REDACTED]", "status": "clean"},
    }
