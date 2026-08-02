from app.services.redact import redact_secrets, scrub_secret_text


def test_recursive_redaction_drops_secret_values_without_mutating_input() -> None:
    raw = {
        "decoy_id": "scholarship",
        "password": "correct horse battery staple",
        "nested": {
            "ssn": "111-22-3333",
            "items": [
                {"token": "header.payload.signature"},
                {"routing_number": "021000021"},
            ],
        },
    }

    clean = redact_secrets(raw)

    assert raw["password"] == "correct horse battery staple"
    assert "password" not in clean
    assert clean["password_entered"] is True
    assert "ssn" not in clean["nested"]
    assert clean["nested"]["ssn_entered"] is True
    assert clean["nested"]["items"][0] == {"token_entered": True}
    assert clean["nested"]["items"][1] == {"bank_data_entered": True}
    assert "correct horse" not in repr(clean)
    assert "111-22-3333" not in repr(clean)
    assert "header.payload.signature" not in repr(clean)
    assert "021000021" not in repr(clean)


def test_safe_flags_and_field_names_are_preserved() -> None:
    event = {
        "fields_present": ["email", "password", "ssn", "routing_number"],
        "password_entered": True,
        "ssn_entered": True,
        "token_entered": False,
        "bank_data_entered": True,
    }

    assert redact_secrets(event) == event


def test_log_scrubber_removes_assignments_and_bearer_values() -> None:
    message = (
        "password=hunter2 token: abc.def authorization=BearerToken "
        "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig"
    )

    clean = scrub_secret_text(message)

    assert "hunter2" not in clean
    assert "abc.def" not in clean
    assert "BearerToken" not in clean
    assert "eyJhbGci" not in clean
    assert clean.count("[REDACTED]") >= 4
