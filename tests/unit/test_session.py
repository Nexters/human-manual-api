from datetime import UTC, datetime, timedelta

import pytest

from pakit.core.session import InvalidSessionError, SessionSigner


def test_creates_and_verifies_a_signed_session() -> None:
    now = datetime(2026, 9, 1, tzinfo=UTC)
    signer = SessionSigner("test-session-secret", max_age_seconds=60)

    token = signer.create(42, now=now)

    assert signer.verify(token, now=now + timedelta(seconds=59)) == 42


@pytest.mark.parametrize("token", ["invalid", "payload.signature", ".."])
def test_rejects_an_invalid_session(token: str) -> None:
    signer = SessionSigner("test-session-secret", max_age_seconds=60)

    with pytest.raises(InvalidSessionError):
        signer.verify(token)


def test_rejects_an_expired_session() -> None:
    now = datetime(2026, 9, 1, tzinfo=UTC)
    signer = SessionSigner("test-session-secret", max_age_seconds=60)
    token = signer.create(42, now=now)

    with pytest.raises(InvalidSessionError):
        signer.verify(token, now=now + timedelta(seconds=60))


def test_requires_a_session_secret() -> None:
    with pytest.raises(ValueError, match="세션 서명 키"):
        SessionSigner("", max_age_seconds=60)
