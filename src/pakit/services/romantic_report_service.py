import re
import secrets
from dataclasses import asdict, dataclass
from importlib.resources import files
from typing import Final

from pakit.services.romantic_profile_builder import (
    PROFILE_VERSION,
    RomanticProfile,
    build_romantic_profile,
)
from pakit.services.romantic_report_generator import (
    RomanticReportGenerationError,
    RomanticReportGenerator,
)
from pakit.services.romantic_report_repository import (
    RomanticReportRepository,
    RomanticReportToSave,
    StoredRomanticReport,
)

PROMPT_VERSION: Final = "romantic-prompt-2026-09-10.1"


class RomanticReportResultNotFoundError(RuntimeError):
    """관계 설명서에 사용할 결과 코드를 찾을 수 없습니다."""


@dataclass(frozen=True)
class CreateRomanticReportCommand:
    mine_result_code: str
    partner_result_code: str
    mine_gender: str
    partner_gender: str


async def create_romantic_report(
    command: CreateRomanticReportCommand,
    repository: RomanticReportRepository,
    generator: RomanticReportGenerator,
) -> StoredRomanticReport:
    existing = await repository.find_existing(
        mine_result_code=command.mine_result_code,
        partner_result_code=command.partner_result_code,
        mine_gender=command.mine_gender,
        partner_gender=command.partner_gender,
        prompt_version=PROMPT_VERSION,
        profile_version=PROFILE_VERSION,
        model=generator.model,
    )
    if existing is not None:
        return existing

    mine_source = await repository.get_profile_source(command.mine_result_code)
    partner_source = await repository.get_profile_source(command.partner_result_code)
    if mine_source is None or partner_source is None:
        raise RomanticReportResultNotFoundError
    mine = build_romantic_profile(mine_source, gender=command.mine_gender)
    partner = build_romantic_profile(partner_source, gender=command.partner_gender)
    instructions, user_prompt = render_prompts(mine, partner)
    generated = await generator.generate(
        instructions=instructions,
        user_prompt=user_prompt,
    )
    _validate_generated_content(generated.content)
    return await repository.save(
        RomanticReportToSave(
            report_code=_new_report_code(),
            mine_result_code=command.mine_result_code,
            partner_result_code=command.partner_result_code,
            mine_gender=command.mine_gender,
            partner_gender=command.partner_gender,
            prompt_version=PROMPT_VERSION,
            profile_version=PROFILE_VERSION,
            model=generator.model,
            input_snapshot={
                "mine": asdict(mine),
                "partner": asdict(partner),
            },
            content=generated.content,
            provider_response_id=generated.provider_response_id,
            input_tokens=generated.input_tokens,
            output_tokens=generated.output_tokens,
        )
    )


def render_prompts(mine: RomanticProfile, partner: RomanticProfile) -> tuple[str, str]:
    root = files("pakit.prompts.relationship")
    instructions = root.joinpath("romantic-system.md").read_text(encoding="utf-8")
    template = root.joinpath("romantic-user-template.md").read_text(encoding="utf-8")
    replacements = {
        "{{participant_a_name}}": mine.name,
        "{{participant_a_gender}}": mine.gender,
        "{{participant_a_mbti}}": mine.mbti,
        "{{participant_a_profile}}": mine.render(),
        "{{participant_b_name}}": partner.name,
        "{{participant_b_gender}}": partner.gender,
        "{{participant_b_mbti}}": partner.mbti,
        "{{participant_b_profile}}": partner.render(),
    }
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    return instructions, template


def _new_report_code() -> str:
    return secrets.token_urlsafe(9)[:12]


def _validate_generated_content(content: str) -> None:
    headings = re.findall(r"^##\s+(\d+)\.\s+(.+?)\s*$", content, flags=re.MULTILINE)
    if [number for number, _ in headings] != [str(number) for number in range(1, 11)]:
        raise RomanticReportGenerationError
    fixed = {
        "1": "이 관계의 핵심 구조",
        "7": "이 관계가 가진 힘",
        "8": "서로에게 해주면 좋은 것",
        "9": "둘만의 관계 규칙",
        "10": "이 관계의 성장 방향",
    }
    if any(dict(headings).get(number) != title for number, title in fixed.items()):
        raise RomanticReportGenerationError
