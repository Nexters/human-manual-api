import pytest

from pakit.services.romantic_report_generator import RomanticReportGenerationError
from pakit.services.romantic_report_service import _validate_generated_content


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
