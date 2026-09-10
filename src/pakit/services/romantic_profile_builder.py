from dataclasses import dataclass
from typing import Final

from pakit.domain.assessment_contract import ASSESSMENT_VERSION
from pakit.services.romantic_report_repository import RelationshipProfileSource

PROFILE_VERSION: Final = "romantic-profile-2026-09-11.10"


class RomanticProfileUnavailableError(RuntimeError):
    """저장된 원본이 현재 프로필 규칙으로 해석될 수 없습니다."""


@dataclass(frozen=True)
class RomanticProfile:
    name: str
    mbti: str
    gender: str
    paragraphs: tuple[str, ...]

    def render(self) -> str:
        return "\n".join(f"- {paragraph}" for paragraph in self.paragraphs)


APPROACH = {
    "inspect_profile": "마음에 드는 사람이 생겨도 곧바로 다가가기보다 상대를 충분히 살피며 마음을 키우는 편이다.",
    "approach_directly": "마음에 드는 사람이 생기면 먼저 다가가는 편이다.",
}
CONFLICT = {
    "hint_and_wait": "서운한 일이 생기면 달라진 기색으로 마음을 알아주길 기다릴 수 있다.",
    "resolve_immediately": "서운한 일이 생기면 그 자리에서 뜻을 확인하고 풀고 싶어 한다.",
}
MESSAGE = {
    "rehearse_with_ai": "다툰 뒤 보낼 말은 여러 번 조언을 구하고 표현을 정리한 뒤 전하는 쪽이라, 대화를 시작하기까지 시간이 필요할 수 있다.",
    "send_immediately": "다툰 뒤 보낼 말이 생겼을 때도 여러 번 검토하거나 조언을 구하기보다 생각한 내용을 곧바로 전하는 쪽이라, 상대에게는 대화를 시작하는 속도가 빠르게 느껴질 수 있다.",
}
SHARING = {
    "share_everything": "소소한 일상을 세밀하게 나누는 일도 가까움을 확인하는 중요한 신호가 될 수 있다.",
    "share_selectively": "소소한 일상을 모두 공유하기보다 필요한 이야기를 선택해서 나누는 쪽에 가깝다.",
}
SUPPORT = {
    "listen_to_me": "힘든 순간에는 해결책보다 무슨 일이 있었는지 천천히 말하고 자신의 감정이 충분히 받아들여지는 도움을 반갑게 느끼는 편이다.",
    "take_me_out": "힘든 순간에는 혼자 생각에 머무르기보다 맛있는 것을 먹거나 바깥바람을 쐬며 기분을 환기하도록 이끄는 도움을 반갑게 느끼는 편이다.",
    "give_me_space": "힘든 순간에는 곧바로 답을 요구받기보다 혼자 정리할 시간을 보장받고 준비되었을 때 다시 연결되는 도움을 반갑게 느끼는 편이다.",
    "solve_together": "힘든 순간에는 감정에만 오래 머무르기보다 무엇이 막혀 있는지 함께 짚고 해결 방법을 찾는 도움을 반갑게 느끼는 편이다.",
    "make_me_laugh": "힘든 순간에는 무거운 분위기를 잠시 내려놓게 해주는 유머와 가벼운 반응에서 다시 숨 쉴 틈을 얻는 편이다.",
}
AFFECTION = {
    "express_with_words": "다정한 말과 반응, 표정처럼 상대가 바로 알아차릴 수 있는 표현으로 관심과 애정을 보여주는 편이다.",
    "express_with_actions": "관심과 애정을 긴 말보다 실제 행동과 챙김으로 보여주는 편이다. 자신이 움직여준 것이 충분한 마음 표현이라고 느낄 수 있다.",
}
TRIGGER = {
    "rush": "재촉받을 때 특히 압박을 느낄 수 있다",
    "interrupt": "자신의 말이 끝나기 전에 끊기는 상황에서 특히 마음이 닫힐 수 있다",
    "take_food": "자기 몫이나 경계를 가볍게 침범당하는 상황에서 특히 불편함을 느낄 수 있다",
    "arrive_late": "약속 시간을 가볍게 넘기는 상황에서 존중받지 못했다고 느낄 수 있다",
    "nag": "반복해서 간섭하거나 잔소리하는 상황에서 특히 답답함을 느낄 수 있다",
    "change_plan": "합의 없이 자신의 계획이 바뀌는 상황에서 통제권을 빼앗긴 듯 답답할 수 있다",
}
REST = {
    "sleep_until_noon": "쉬는 날에는 늦게까지 충분히 자며 회복하는 시간을 좋아한다",
    "morning_run": "쉬는 날에도 아침에 몸을 움직이며 리듬을 되찾는 편이다",
    "brunch_cafe": "쉬는 날에는 여유롭게 먹고 공간을 즐기는 시간에서 기분을 회복한다",
    "stay_in_bed": "쉬는 날에는 이불 속에서 충분히 늘어져 회복하는 시간을 좋아한다",
    "watch_streaming": "쉬는 날에는 미뤄둔 콘텐츠를 몰입해 보며 머리를 식힌다",
    "self_development": "쉬는 날에도 배우거나 자신을 정돈하는 활동에서 만족과 동력을 얻는다",
}
REACTION = {
    "ruminate": "사람들 앞에서 건넨 말에 반응이 없으면 그 장면을 오래 곱씹을 수 있다",
    "forget_quickly": "사람들 앞에서 건넨 말에 반응이 없어도 비교적 빨리 넘기는 편이다",
}


def build_romantic_profile(source: RelationshipProfileSource, *, gender: str) -> RomanticProfile:
    if source.assessment_version != ASSESSMENT_VERSION:
        raise RomanticProfileUnavailableError
    answers = source.answers
    try:
        distance = int(answers["step2.q04"])
        paragraphs = (
            "연인과 얼마나 자주 연결되고 일상을 함께 나누고 싶은지를 기준으로, "
            "각자의 시간과 영역을 중시하는 쪽을 0, 늘 함께하며 세밀하게 공유하는 쪽을 "
            f"100으로 놓았을 때 {distance} 정도의 가까움을 편하게 느낀다. "
            f"{SHARING[str(answers['step2.q05'])]}",
            APPROACH[str(answers["step2.q01"])],
            f"{CONFLICT[str(answers['step2.q02'])]} {MESSAGE[str(answers['step2.q03'])]}",
            SUPPORT[str(answers["step1.q12"])],
            AFFECTION[str(answers["step2.q08"])],
            f"{REST[str(answers['step1.q07'])]}. "
            "(이 정보는 단편적으로 믿지 말고 MBTI와 결합해서 사용하세요)",
            f"{TRIGGER[str(answers['step1.q06'])]}. "
            "(이 정보는 단편적으로 믿지 말고 MBTI와 결합해서 사용하세요)",
            f"{_routine_pattern(source.axis_scores['routine'])} "
            f"{REACTION[str(answers['step2.q09'])]}.",
        )
    except (KeyError, TypeError, ValueError) as error:
        raise RomanticProfileUnavailableError from error
    return RomanticProfile(
        name=_safe_name(source.nickname),
        mbti=source.mbti,
        gender=gender,
        paragraphs=paragraphs,
    )


def _safe_name(value: str) -> str:
    return " ".join(value.split())[:30] or "A"


def _routine_pattern(score: int) -> str:
    if score < 50:
        return "익숙한 방식에 머무르기보다 새로운 선택과 경험을 탐험하는 편이다."
    return "새로운 것을 계속 탐험하기보다 익숙하고 검증된 선택과 흐름을 편하게 여긴다."
