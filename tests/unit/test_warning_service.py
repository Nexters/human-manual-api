import pytest

from pakit.domain.assessment import MbtiType
from pakit.services.warning_service import build_warnings


def test_builds_four_warnings_in_fixed_order() -> None:
    assert build_warnings(
        protected_time="after_waking",
        anger_trigger="rush",
        mbti=MbtiType.ENTP,
    ) == (
        "해결하려고 꺼낸 말에 차갑다는 반응이 돌아오면 억울해져요",
        "내 얘기에 반응이 없으면 신나서 하던 이야기도 금세 재미없어져요",
        "재촉받으면 하려던 마음도 사라져요",
        "잠이 덜 깨면 첫 반응이 무뚝뚝해요",
    )


@pytest.mark.parametrize(
    ("protected_time", "expected"),
    [
        ("after_waking", "잠이 덜 깨면 첫 반응이 무뚝뚝해요"),
        ("during_meal", "밥 먹는 흐름이 끊기면 바로 예민해져요"),
        ("after_work", "퇴근 직후 할 일이 쏟아지면 바로 방전돼요"),
        ("late_night", "새벽 감성을 끊으면 괜히 더 예민해져요"),
    ],
)
def test_maps_every_protected_time(protected_time: str, expected: str) -> None:
    assert build_warnings(protected_time, "rush", MbtiType.ENTP)[3] == expected


@pytest.mark.parametrize(
    ("anger_trigger", "expected"),
    [
        ("rush", "재촉받으면 하려던 마음도 사라져요"),
        ("interrupt", "말을 끊으면 남은 이야기도 삼켜버려요"),
        ("take_food", "음식을 허락 없이 가져가면 한입보다 큰 서운함이 남아요"),
        ("arrive_late", "늦고도 태연하면 기다린 만큼 신뢰가 깎여요"),
        ("nag", "잔소리가 반복되면 귀부터 닫아요"),
        ("change_plan", "계획이 갑자기 바뀌면 기분부터 틀어져요"),
    ],
)
def test_maps_every_anger_trigger(anger_trigger: str, expected: str) -> None:
    assert build_warnings("after_waking", anger_trigger, MbtiType.ENTP)[2] == expected


@pytest.mark.parametrize(
    ("mbti", "social_energy", "communication"),
    [
        (
            MbtiType.ENTP,
            "내 얘기에 반응이 없으면 신나서 하던 이야기도 금세 재미없어져요",
            "해결하려고 꺼낸 말에 차갑다는 반응이 돌아오면 억울해져요",
        ),
        (
            MbtiType.INTP,
            "혼자 정리할 틈이 없으면 대답이 점점 짧아져요",
            "해결하려고 꺼낸 말에 차갑다는 반응이 돌아오면 억울해져요",
        ),
        (
            MbtiType.ENFP,
            "내 얘기에 반응이 없으면 신나서 하던 이야기도 금세 재미없어져요",
            "진심을 꺼냈는데 예민하다는 말이 돌아오면 오래 마음에 남아요",
        ),
        (
            MbtiType.INFP,
            "혼자 정리할 틈이 없으면 대답이 점점 짧아져요",
            "진심을 꺼냈는데 예민하다는 말이 돌아오면 오래 마음에 남아요",
        ),
    ],
)
def test_uses_mbti_energy_and_communication_axes(
    mbti: MbtiType,
    social_energy: str,
    communication: str,
) -> None:
    result = build_warnings("after_waking", "rush", mbti)

    assert result[:2] == (communication, social_energy)
