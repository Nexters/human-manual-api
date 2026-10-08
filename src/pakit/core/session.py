import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta


class InvalidSessionError(ValueError):
    pass


class SessionSigner:
    def __init__(self, secret: str, *, max_age_seconds: int) -> None:
        if not secret:
            raise ValueError("세션 서명 키가 설정되지 않았습니다.")
        self._secret = secret.encode()
        self._max_age_seconds = max_age_seconds

    def create(
        self,
        user_id: int,
        *,
        now: datetime | None = None,
        max_age_seconds: int | None = None,
    ) -> str:
        issued_at = now or datetime.now(UTC)
        requested_age = self._max_age_seconds if max_age_seconds is None else max_age_seconds
        session_age = min(requested_age, self._max_age_seconds)
        expires_at = issued_at + timedelta(seconds=session_age)
        payload = json.dumps(
            {"user_id": user_id, "exp": int(expires_at.timestamp())},
            separators=(",", ":"),
        ).encode()
        encoded = base64.urlsafe_b64encode(payload).rstrip(b"=")
        signature = hmac.new(self._secret, encoded, hashlib.sha256).digest()
        return f"{encoded.decode()}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"

    def verify(self, token: str, *, now: datetime | None = None) -> int:
        try:
            encoded, encoded_signature = token.split(".", maxsplit=1)
            expected = hmac.new(self._secret, encoded.encode(), hashlib.sha256).digest()
            signature = _decode_base64(encoded_signature)
            if not hmac.compare_digest(signature, expected):
                raise InvalidSessionError
            payload = json.loads(_decode_base64(encoded).decode())
            user_id = payload["user_id"]
            expires_at = payload["exp"]
            if not isinstance(user_id, int) or not isinstance(expires_at, int):
                raise InvalidSessionError
            current_time = now or datetime.now(UTC)
            if int(current_time.timestamp()) >= expires_at:
                raise InvalidSessionError
            return user_id
        except (ValueError, KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
            raise InvalidSessionError from error


def _decode_base64(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
