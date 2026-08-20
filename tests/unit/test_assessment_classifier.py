import pytest

from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_submission import AssessmentSubmission, SubmittedAnswer
from pakit.services.assessment_classifier import (
    ADJECTIVES,
    classify_submission,
    opening_tool_code,
    packaging_code,
)


def _submission(overrides: dict[str, str | int] | None = None) -> AssessmentSubmission:
    values: dict[str, str | int] = {
        "step2.q01": "inspect_profile",
        "step2.q02": "hint_and_wait",
        "step2.q03": "rehearse_with_ai",
        "step2.q04": 50,
        "step2.q05": "share_everything",
        "step2.q06": 247,
        "step2.q07": "decorate_for_mood",
        "step2.q08": "express_with_words",
        "step2.q09": "ruminate",
        "step2.q10": "order_familiar_menu",
        "step2.q11": "order_familiar_stores",
        "step2.q12": "press",
    }
    values.update(overrides or {})
    return AssessmentSubmission(
        assessment_version="test",
        nickname="테스터",
        answers=tuple(SubmittedAnswer(question_id, value) for question_id, value in values.items()),
        mbti=MbtiType.ENTP,
    )


def test_scores_axes_and_selects_adjective_from_submission() -> None:
    result = classify_submission(_submission())

    assert result.axis_scores.attachment == 75
    assert result.axis_scores.expression == 0
    assert result.axis_scores.routine == 67
    assert result.axis_scores.egen == 100
    assert result.packaging_code == "A3"
    assert result.opening_tool_code == "B1"
    assert result.adjective == "옷 예쁘게 입고 플러팅 했다고 하는"


def test_scores_are_independent_of_frontend_display_order() -> None:
    submission = _submission()
    answers_by_id = {answer.question_id: answer for answer in submission.answers}
    display_order = [
        "step2.q01",
        "step2.q02",
        "step2.q03",
        "step2.q04",
        "step2.q05",
        "step2.q06",
        "step2.q10",
        "step2.q07",
        "step2.q08",
        "step2.q09",
        "step2.q11",
        "step2.q12",
    ]
    reordered_submission = AssessmentSubmission(
        assessment_version=submission.assessment_version,
        nickname=submission.nickname,
        answers=tuple(answers_by_id[question_id] for question_id in display_order),
        mbti=submission.mbti,
    )

    assert classify_submission(reordered_submission) == classify_submission(submission)


def test_treats_exactly_300_messages_as_neutral_signal() -> None:
    result = classify_submission(
        _submission(
            {
                "step2.q04": 100,
                "step2.q05": "share_selectively",
                "step2.q06": 300,
            }
        )
    )

    assert result.axis_scores.attachment == 10


@pytest.mark.parametrize(
    ("q04", "q05", "q06", "expected"),
    [
        (0, "share_selectively", 999, 50),
        (100, "share_everything", 0, 50),
        (25, "share_selectively", 999, 38),
        (75, "share_everything", 0, 63),
    ],
)
def test_weights_attachment_inputs_50_30_20(
    q04: int,
    q05: str,
    q06: int,
    expected: int,
) -> None:
    result = classify_submission(
        _submission({"step2.q04": q04, "step2.q05": q05, "step2.q06": q06})
    )

    assert result.axis_scores.attachment == expected


@pytest.mark.parametrize(
    ("expression", "attachment", "expected"),
    [
        (50, 50, "A1"),
        (50, 49, "A2"),
        (49, 50, "A3"),
        (49, 49, "A4"),
    ],
)
def test_selects_packaging_at_50_point_boundary(
    expression: int, attachment: int, expected: str
) -> None:
    assert packaging_code(expression, attachment) == expected


@pytest.mark.parametrize(
    ("routine", "egen", "expected"),
    [
        (50, 50, "B1"),
        (50, 49, "B2"),
        (49, 50, "B3"),
        (49, 49, "B4"),
    ],
)
def test_selects_opening_tool_at_50_point_boundary(routine: int, egen: int, expected: str) -> None:
    assert opening_tool_code(routine, egen) == expected


def test_defines_one_adjective_for_every_subitem_combination() -> None:
    assert set(ADJECTIVES) == {
        (f"A{packaging}", f"B{tool}") for packaging in range(1, 5) for tool in range(1, 5)
    }
