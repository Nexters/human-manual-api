from dataclasses import dataclass

from pakit.domain.assessment_submission import (
    AssessmentSubmission,
    AxisScoresData,
)

ADJECTIVES: dict[tuple[str, str], str] = {
    ("A1", "B1"): "좋아하면 프사에 티 내고 대놓고 자랑하는",
    ("A1", "B2"): "물어보면 팩트부터 날리고 밥은 사주는",
    ("A1", "B3"): "좋으면 새벽 2시에도 카톡 폭탄 보내는",
    ("A1", "B4"): "꽂히면 그날 바로 번호 따는",
    ("A2", "B1"): "먼저 연락은 안 하면서 생일은 챙기는",
    ("A2", "B2"): "지적도 매뉴얼인",
    ("A2", "B3"): '"언제 한번 밥 먹자"만 3만 번 말하는',
    ("A2", "B4"): '"어디야" 물을 때마다 다른 나라 가 있는',
    ("A3", "B1"): "옷 예쁘게 입고 플러팅 했다고 하는",
    ("A3", "B2"): "답장은 'ㅇㅇ'인데 읽씹은 안 하는",
    ("A3", "B3"): "3년 전 게시물까지 정독하고 안부도 꼬박 묻는",
    ("A3", "B4"): "번따하는 상상만 오만 번 해본",
    ("A4", "B1"): "낯가리지만 친해지면 말 많은",
    ("A4", "B2"): "답장 3일 뒤에 오고 프사도 안 바꾸는",
    ("A4", "B3"): "연애 시뮬 10번 하고 첫 데이트 나가는",
    ("A4", "B4"): "뭐 하고 사는지 아무도 모르는",
}


@dataclass(frozen=True)
class AssessmentClassification:
    axis_scores: AxisScoresData
    packaging_code: str
    opening_tool_code: str
    adjective: str


def _rounded_mean(*scores: int) -> int:
    return (sum(scores) + len(scores) // 2) // len(scores)


def _choice_score(value: str, score_100_value: str) -> int:
    return 100 if value == score_100_value else 0


def _message_count_score(value: int) -> int:
    if value < 300:
        return 100
    if value > 300:
        return 0
    return 50


def packaging_code(expression: int, attachment: int) -> str:
    if expression >= 50:
        return "A1" if attachment >= 50 else "A2"
    return "A3" if attachment >= 50 else "A4"


def opening_tool_code(routine: int, egen: int) -> str:
    if routine >= 50:
        return "B1" if egen >= 50 else "B2"
    return "B3" if egen >= 50 else "B4"


def classify_submission(submission: AssessmentSubmission) -> AssessmentClassification:
    answers = {answer.question_id: answer.value for answer in submission.answers}

    expression = _rounded_mean(
        _choice_score(str(answers["step2.q01"]), "approach_directly"),
        _choice_score(str(answers["step2.q02"]), "resolve_immediately"),
        _choice_score(str(answers["step2.q03"]), "send_immediately"),
    )
    attachment = _rounded_mean(
        100 - int(answers["step2.q04"]),
        _choice_score(str(answers["step2.q05"]), "share_everything"),
        _message_count_score(int(answers["step2.q06"])),
    )
    egen = _rounded_mean(
        _choice_score(str(answers["step2.q07"]), "decorate_for_mood"),
        _choice_score(str(answers["step2.q08"]), "express_with_words"),
        _choice_score(str(answers["step2.q09"]), "ruminate"),
    )
    routine = _rounded_mean(
        _choice_score(str(answers["step2.q10"]), "order_familiar_menu"),
        _choice_score(str(answers["step2.q11"]), "order_familiar_stores"),
        _choice_score(str(answers["step2.q12"]), "skip"),
    )

    axis_scores = AxisScoresData(
        attachment=attachment,
        expression=expression,
        routine=routine,
        egen=egen,
    )
    selected_packaging_code = packaging_code(expression, attachment)
    selected_opening_tool_code = opening_tool_code(routine, egen)

    return AssessmentClassification(
        axis_scores=axis_scores,
        packaging_code=selected_packaging_code,
        opening_tool_code=selected_opening_tool_code,
        adjective=ADJECTIVES[(selected_packaging_code, selected_opening_tool_code)],
    )
