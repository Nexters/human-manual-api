import pytest

from pakit.domain.assessment import MbtiType
from pakit.services.warning_service import build_warnings


def test_builds_four_warnings_in_fixed_order() -> None:
    assert build_warnings(
        anger_trigger="rush",
        mbti=MbtiType.ENTP,
    ) == (
        "해결하려고 꺼낸 말에 차갑다는 말이 돌아오면 억울해져요",
        "내 얘기에 반응이 없으면 신나서 하던 이야기도 금세 재미없어져요",
        "재촉받으면 하려던 마음도 사라져요",
        '내 아이디어에 "그건 원래 안 돼"라고 하면, 끝까지 뒤집어 보여주고 싶어져요',
    )


@pytest.mark.parametrize(
    ("mbti", "expected"),
    [
        (
            MbtiType.INTJ,
            '근거도 없이 "아니 그냥 내 말이 맞아"라고 우기면, 그 자리에서 말이 끊겨요',
        ),
        (
            MbtiType.INTP,
            '대충 아는 걸로 "그거 원래 이런 거잖아"라며 아는 척하면, '
            "납득할 때까지 머리가 안 꺼져요",
        ),
        (
            MbtiType.ENTJ,
            '다 아는 얘기를 "이건 이렇게 하는 거야"라며 가르치려 들면, '
            "듣는 척만 하고 마음이 떠나요",
        ),
        (
            MbtiType.ENTP,
            '내 아이디어에 "그건 원래 안 돼"라고 하면, 끝까지 뒤집어 보여주고 싶어져요',
        ),
        (
            MbtiType.INFJ,
            '무례한 행동을 해놓고 "예민하게 굴지 마"라고 하면, 그 사람한테만 문이 닫혀요',
        ),
        (
            MbtiType.INFP,
            '속마음을 말하는데 "그건 팩트잖아"라며 눌러버리면, 맞는 말이어도 오래 아파요',
        ),
        (
            MbtiType.ENFJ,
            '좋게 풀어보려고 나섰는데 "네가 무슨 상관인데"라고 선을 그으면, '
            "며칠씩 그 말이 안 잊혀요",
        ),
        (
            MbtiType.ENFP,
            '선 넘는 장난을 "농담인데 왜 정색해"라며 계속하면, 텐션이 급속 방전돼요',
        ),
        (
            MbtiType.ISTJ,
            '정해둔 약속을 계속 어겨놓고 "뭐 어때"라고 하면, 신뢰 잔량이 확 깎여요',
        ),
        (
            MbtiType.ISFJ,
            "나 말고 내 가까운 사람을 건드리면, 그때부터 웃는 얼굴이 안 나와요",
        ),
        (
            MbtiType.ESTJ,
            '해보지도 않고 "어차피 안 될걸"이라고 하면, 정색 모드가 바로 켜져요',
        ),
        (
            MbtiType.ESFJ,
            '내가 챙겨준 걸 "원래 네가 하는 거잖아"라고 넘기면, 웃고 있어도 속으로 쌓여요',
        ),
        (
            MbtiType.ISTP,
            '"그래서 지금 기분이 어떤데"라며 감정 표현을 강요하면, 대답이 점점 짧아져요',
        ),
        (
            MbtiType.ISFP,
            '내 속도로 가는데 "왜 이렇게 느려"라고 재촉하면, 하려던 마음이 강제 종료돼요',
        ),
        (MbtiType.ESTP, "할 말을 빙빙 돌리며 결론을 안 내면, 인내심 잔량이 0%가 돼요"),
        (
            MbtiType.ESFP,
            '분위기 좋았는데 "좀 조용히 해"라며 눈치를 주면, 그 자리 전원이 같이 꺼져요',
        ),
    ],
)
def test_maps_every_mbti_trigger(mbti: MbtiType, expected: str) -> None:
    assert build_warnings("rush", mbti)[3] == expected


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
    assert build_warnings(anger_trigger, MbtiType.ENTP)[2] == expected


@pytest.mark.parametrize(
    ("mbti", "social_energy", "communication"),
    [
        (
            MbtiType.ENTP,
            "내 얘기에 반응이 없으면 신나서 하던 이야기도 금세 재미없어져요",
            "해결하려고 꺼낸 말에 차갑다는 말이 돌아오면 억울해져요",
        ),
        (
            MbtiType.INTP,
            "혼자 정리할 틈이 없으면 대답이 점점 짧아져요",
            "해결하려고 꺼낸 말에 차갑다는 말이 돌아오면 억울해져요",
        ),
        (
            MbtiType.ENFP,
            "내 얘기에 반응이 없으면 신나서 하던 이야기도 금세 재미없어져요",
            "속마음을 꺼냈는데 유난이라는 말이 돌아오면 오래 마음에 남아요",
        ),
        (
            MbtiType.INFP,
            "혼자 정리할 틈이 없으면 대답이 점점 짧아져요",
            "속마음을 꺼냈는데 유난이라는 말이 돌아오면 오래 마음에 남아요",
        ),
    ],
)
def test_uses_mbti_energy_and_communication_axes(
    mbti: MbtiType,
    social_energy: str,
    communication: str,
) -> None:
    result = build_warnings("rush", mbti)

    assert result[:2] == (communication, social_energy)
