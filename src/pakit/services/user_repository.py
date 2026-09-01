from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class StoredUser:
    id: int
    created_at: datetime
    last_logged_in_at: datetime


@dataclass(frozen=True)
class UserResultSummary:
    result_code: str
    nickname: str | None
    result_name: str
    noun: str
    character_id: str
    image_url: str
    created_at: datetime


@dataclass(frozen=True)
class UserCompatibilitySummary:
    mine: UserResultSummary
    friend: UserResultSummary
    score: int
    tested_at: datetime


@dataclass(frozen=True)
class ResultSyncSummary:
    synced: tuple[str, ...]
    already_synced: tuple[str, ...]
    rejected: tuple[str, ...]


class UserRepository(Protocol):
    async def upsert_kakao_user(self, kakao_user_id: str) -> StoredUser: ...

    async def get_user(self, user_id: int) -> StoredUser | None: ...

    async def sync_results(
        self,
        user_id: int,
        result_codes: tuple[str, ...],
    ) -> ResultSyncSummary: ...

    async def list_results(self, user_id: int) -> list[UserResultSummary]: ...

    async def list_compatibilities(self, user_id: int) -> list[UserCompatibilitySummary]: ...
