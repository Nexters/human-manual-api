import pytest

from pakit.services.romantic_profile_builder import RomanticProfile
from pakit.services.romantic_report_generator import RomanticReportGenerationError
from pakit.services.romantic_report_service import (
    PROMPT_VERSION,
    _validate_generated_content,
    render_prompts,
)


def test_rejects_generated_report_missing_required_sections() -> None:
    with pytest.raises(RomanticReportGenerationError):
        _validate_generated_content("## 1. 이 관계의 핵심 구조\n\n본문")


def test_accepts_generated_report_with_ten_sections() -> None:
    headings = [
        "이 관계의 핵심 구조",
        "주제 2",
        "주제 3",
        "주제 4",
        "주제 5",
        "주제 6",
        "이 관계가 가진 힘",
        "서로에게 해주면 좋은 것",
        "둘만의 관계 규칙",
        "이 관계의 성장 방향",
    ]
    content = "\n\n".join(
        f"## {number}. {heading}\n\n본문" for number, heading in enumerate(headings, start=1)
    )

    _validate_generated_content(content)


def test_prompt_requires_names_for_each_participants_reaction() -> None:
    mine = RomanticProfile(
        name="T엔팁",
        mbti="ENTP",
        gender="남자",
        paragraphs=("바로 말하는 편이다.",),
    )
    partner = RomanticProfile(
        name="T인팁",
        mbti="INTP",
        gender="남자",
        paragraphs=("생각을 정리한 뒤 말하는 편이다.",),
    )

    instructions, user_prompt = render_prompts(mine, partner)

    assert "행동, 감정, 욕구, 해석의 주체" in instructions
    assert "성별이 같거나 다를 수 있습니다" in instructions
    assert "`T엔팁님`과 `T인팁님`을 모두 쓰세요" in user_prompt
    assert "T인팁님이 기다릴 때" in user_prompt
    assert "T인팁님은 T엔팁님보다" in user_prompt
    assert "“한 사람”, “다른 사람”, “한쪽”" in user_prompt
    assert "{{participant_a_name}}" not in user_prompt
    assert PROMPT_VERSION == "romantic-prompt-2026-10-08.1"
