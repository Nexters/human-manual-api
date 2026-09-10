import pytest

from pakit.services.romantic_profile_builder import _routine_pattern, build_romantic_profile
from pakit.services.romantic_report_repository import RelationshipProfileSource


def test_builds_natural_profile_without_question_codes() -> None:
    source = RelationshipProfileSource(
        result_code="GU26BwcL",
        nickname="해서니",
        mbti="ENTP",
        assessment_version="2026-08-20.1",
        axis_scores={"attachment": 13, "expression": 100, "routine": 0, "egen": 33},
        answers={
            "step1.q01": "hangout",
            "step1.q02": "make_it_happen",
            "step1.q05": "late_night",
            "step1.q06": "nag",
            "step1.q07": "stay_in_bed",
            "step1.q08": "go_for_drive",
            "step1.q11": "last_chance",
            "step1.q12": "solve_together",
            "step2.q01": "approach_directly",
            "step2.q02": "resolve_immediately",
            "step2.q03": "send_immediately",
            "step2.q04": 75,
            "step2.q05": "share_selectively",
            "step2.q06": 400,
            "step2.q07": "decorate_for_mood",
            "step2.q08": "express_with_actions",
            "step2.q09": "forget_quickly",
            "step2.q10": "try_new_menu",
            "step2.q11": "try_new_store",
            "step2.q12": "press",
        },
    )

    profile = build_romantic_profile(source, gender="여자")
    rendered = profile.render()

    assert "각자의 시간과 영역을 중시하는 쪽을 0" in rendered
    assert "늘 함께하며 세밀하게 공유하는 쪽을 100으로 놓았을 때 75" in rendered
    assert "75 정도의 가까움을 편하게 느낀다" in rendered
    assert "마음에 드는 사람이 생기면 먼저 다가가는 편이다." in rendered
    assert "생각한 내용을 곧바로 전하는 쪽" in rendered
    assert "생각이나 감정도 오래 살핀 뒤" not in rendered
    assert "친구와" not in rendered
    assert "step1" not in rendered
    assert "골랐" not in rendered
    assert "늦은 밤" not in rendered
    assert "에겐" not in rendered
    assert "루틴" not in rendered
    assert "새로운 선택과 경험을 탐험하는 편" in rendered
    assert "메뉴에서는" not in rendered
    assert "가게는" not in rendered
    assert "친구들이" not in rendered
    assert "갑자기 시간이" not in rendered
    assert "다시 동력" not in rendered
    assert "조명" not in rendered
    assert "공간" not in rendered
    assert len(profile.paragraphs) == 8


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (49, "새로운 선택과 경험을 탐험하는 편"),
        (50, "익숙하고 검증된 선택과 흐름을 편하게 여긴다"),
    ],
)
def test_classifies_combined_routine_score_at_fifty(score: int, expected: str) -> None:
    assert expected in _routine_pattern(score)
