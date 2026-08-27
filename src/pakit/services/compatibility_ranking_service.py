from dataclasses import dataclass
from datetime import datetime

from pakit.services.result_repository import ResultRepository
from pakit.services.usage_event_repository import CompatibilityEventReader, StoredCompatibilityEvent


class CompatibilityRankingNotFoundError(LookupError):
    """랭킹의 기준이 되는 결과 코드가 존재하지 않습니다."""


@dataclass(frozen=True)
class CompatibilityRankingItemData:
    rank: int
    result_code: str
    nickname: str | None
    result_name: str
    noun: str
    character_id: str
    image_url: str
    score: int
    tested_at: datetime


@dataclass(frozen=True)
class CompatibilityRankingData:
    result_code: str
    total: int
    rankings: tuple[CompatibilityRankingItemData, ...]


def _partner_code(event: StoredCompatibilityEvent, result_code: str) -> str:
    if event.mine_result_code == result_code:
        return event.friend_result_code
    return event.mine_result_code


async def get_compatibility_ranking(
    result_code: str,
    result_repository: ResultRepository,
    event_reader: CompatibilityEventReader,
) -> CompatibilityRankingData:
    """한 결과 코드와 궁합을 완료한 고유 상대를 점수순으로 반환합니다."""
    if await result_repository.get(result_code) is None:
        raise CompatibilityRankingNotFoundError

    events = await event_reader.list_compatibility_events(result_code)
    latest_by_partner: dict[str, StoredCompatibilityEvent] = {}
    for event in events:
        partner_code = _partner_code(event, result_code)
        if partner_code == result_code:
            continue
        current = latest_by_partner.get(partner_code)
        if current is None or event.occurred_at > current.occurred_at:
            latest_by_partner[partner_code] = event

    ranked_candidates: list[tuple[str, str | None, str, str, str, str, int, datetime]] = []
    for partner_code, event in latest_by_partner.items():
        partner = await result_repository.get(partner_code)
        if partner is None:
            continue
        ranked_candidates.append(
            (
                partner_code,
                partner.participant.nickname if partner.participant is not None else None,
                partner.overview.result_name,
                partner.overview.noun,
                partner.overview.character_id,
                partner.overview.image_url,
                event.score,
                event.occurred_at,
            )
        )

    ranked_candidates.sort(key=lambda item: (-item[6], -item[7].timestamp(), item[0]))
    rankings: list[CompatibilityRankingItemData] = []
    previous_score: int | None = None
    previous_rank = 0
    for position, candidate in enumerate(ranked_candidates, start=1):
        partner_code, nickname, result_name, noun, character_id, image_url, score, tested_at = (
            candidate
        )
        rank = previous_rank if score == previous_score else position
        rankings.append(
            CompatibilityRankingItemData(
                rank=rank,
                result_code=partner_code,
                nickname=nickname,
                result_name=result_name,
                noun=noun,
                character_id=character_id,
                image_url=image_url,
                score=score,
                tested_at=tested_at,
            )
        )
        previous_score = score
        previous_rank = rank

    return CompatibilityRankingData(
        result_code=result_code,
        total=len(rankings),
        rankings=tuple(rankings),
    )
