from typing import Protocol

from pakit.services.user_repository import StoredUser, UserRepository


class KakaoClient(Protocol):
    def authorization_url(self, state: str) -> str: ...

    async def get_user_id(self, code: str) -> str: ...


async def log_in_with_kakao(
    code: str,
    kakao_client: KakaoClient,
    repository: UserRepository,
) -> StoredUser:
    kakao_user_id = await kakao_client.get_user_id(code)
    return await repository.upsert_kakao_user(kakao_user_id)
