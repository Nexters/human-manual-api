from dataclasses import dataclass
from enum import StrEnum

ASSESSMENT_VERSION = "2026-08-14.2"


class AnswerKind(StrEnum):
    CHOICE = "choice"
    SCALE = "scale"
    INTEGER = "integer"
    ACTION = "action"


@dataclass(frozen=True)
class QuestionContract:
    answer_kind: AnswerKind
    allowed_values: frozenset[str] = frozenset()
    minimum: int | None = None
    maximum: int | None = None


QUESTION_CONTRACTS: dict[str, QuestionContract] = {
    "step1.q01": QuestionContract(
        AnswerKind.CHOICE, frozenset({"decision", "worries", "hangout", "information"})
    ),
    "step1.q02": QuestionContract(
        AnswerKind.CHOICE,
        frozenset(
            {
                "set_direction",
                "lift_mood",
                "make_it_happen",
                "draw_people_out",
                "coordinate_opinions",
                "remember_and_care",
            }
        ),
    ),
    "step1.q03": QuestionContract(
        AnswerKind.CHOICE,
        frozenset({"save_favorites", "multiple_alarms", "duplicate_clothes", "check_spoilers"}),
    ),
    "step1.q04": QuestionContract(
        AnswerKind.CHOICE,
        frozenset(
            {
                "phone_overuse",
                "sleep_late",
                "overspending",
                "slow_reply",
                "messy_room",
                "low_battery",
            }
        ),
    ),
    "step1.q05": QuestionContract(
        AnswerKind.CHOICE, frozenset({"after_waking", "during_meal", "after_work", "late_night"})
    ),
    "step1.q06": QuestionContract(
        AnswerKind.CHOICE,
        frozenset({"rush", "interrupt", "take_food", "arrive_late", "nag", "change_plan"}),
    ),
    "step1.q07": QuestionContract(
        AnswerKind.CHOICE,
        frozenset(
            {
                "sleep_until_noon",
                "morning_run",
                "brunch_cafe",
                "stay_in_bed",
                "watch_streaming",
                "self_development",
            }
        ),
    ),
    "step1.q08": QuestionContract(
        AnswerKind.CHOICE, frozenset({"go_to_bed", "contact_others", "eat_alone", "go_for_drive"})
    ),
    "step1.q09": QuestionContract(
        AnswerKind.CHOICE, frozenset({"tsundere", "planner", "meme_addict", "foodie"})
    ),
    "step1.q10": QuestionContract(
        AnswerKind.CHOICE,
        frozenset({"morning_person", "no_plan", "photo_obsessed", "hates_walking"}),
    ),
    "step1.q11": QuestionContract(
        AnswerKind.CHOICE,
        frozenset(
            {
                "curiosity",
                "needed_by_someone",
                "clear_goal",
                "responsibility",
                "last_chance",
                "fun",
            }
        ),
    ),
    "step2.q01": QuestionContract(
        AnswerKind.CHOICE, frozenset({"inspect_profile", "approach_directly"})
    ),
    "step2.q02": QuestionContract(
        AnswerKind.CHOICE, frozenset({"hint_and_wait", "resolve_immediately"})
    ),
    "step2.q03": QuestionContract(
        AnswerKind.CHOICE, frozenset({"rehearse_with_ai", "send_immediately"})
    ),
    "step2.q04": QuestionContract(AnswerKind.SCALE, minimum=0, maximum=100),
    "step2.q05": QuestionContract(
        AnswerKind.CHOICE, frozenset({"share_everything", "share_selectively"})
    ),
    "step2.q06": QuestionContract(AnswerKind.INTEGER, minimum=0, maximum=999),
    "step2.q07": QuestionContract(
        AnswerKind.CHOICE, frozenset({"decorate_for_mood", "essentials_only"})
    ),
    "step2.q08": QuestionContract(
        AnswerKind.CHOICE, frozenset({"express_with_words", "express_with_actions"})
    ),
    "step2.q09": QuestionContract(AnswerKind.CHOICE, frozenset({"ruminate", "forget_quickly"})),
    "step2.q10": QuestionContract(
        AnswerKind.CHOICE, frozenset({"order_familiar_menu", "try_new_menu"})
    ),
    "step2.q11": QuestionContract(
        AnswerKind.CHOICE, frozenset({"order_familiar_stores", "try_new_store"})
    ),
    "step2.q12": QuestionContract(AnswerKind.ACTION, frozenset({"press", "skip"})),
}
