from pakit.domain.assessment import MbtiType
from pakit.services.motivation_service import build_motivation_feature
from pakit.services.result_content import (
    MBTI_MIDDLE_GROUP,
    MOTIVATION_COPY,
    MOTIVATION_DESCRIPTION,
)


def test_builds_every_motivation_and_mbti_combination() -> None:
    results = {
        (answer, mbti): build_motivation_feature(answer, mbti)
        for answer in MOTIVATION_COPY
        for mbti in MbtiType
    }

    assert len(results) == 6 * 16
    assert len({feature.description for feature in results.values()}) == 6 * 4
    for (answer, mbti), feature in results.items():
        assert feature.title == MOTIVATION_COPY[answer].title
        group = MBTI_MIDDLE_GROUP[mbti]
        assert feature.description == MOTIVATION_DESCRIPTION[(answer, group)]
        assert feature.description.count(".") == 1
        assert len(feature.description) <= 52


def test_builds_confirmed_curiosity_copy_for_entp() -> None:
    feature = build_motivation_feature("curiosity", MbtiType.ENTP)

    assert feature.title == "궁금한 건 못 참아요"
    assert feature.description == (
        "궁금한 건 검색만으로 넘기지 않고, 원리와 다른 가능성까지 직접 확인해요."
    )


def test_builds_concise_connected_fun_copy_for_entp() -> None:
    feature = build_motivation_feature("fun", MbtiType.ENTP)

    assert feature.description == (
        "재밌는 일이 시작되면 구경만 하지 않고, 더 재밌게 만들 방법까지 보태요."
    )
    assert len(feature.description) <= 50


def test_builds_confirmed_clear_goal_copy_for_every_middle_group() -> None:
    assert {
        group: MOTIVATION_DESCRIPTION[("clear_goal", group)] for group in ("NT", "ST", "NF", "SF")
    } == {
        "NT": (
            "시작한 일은 끝을 봐야 하는 편이라, 마무리 전에 더 나은 방법이 없는지 한 번 더 "
            "따져봐요."
        ),
        "ST": "시작한 일은 끝을 봐야 하는 편이라, 정한 순서대로 밀어붙여 기어이 끝을 내요.",
        "NF": ("시작한 일은 끝을 봐야 하는 편이라, 지칠 때도 처음 마음을 떠올리며 밀고 나가요."),
        "SF": ("시작한 일은 끝을 봐야 하는 편이라, 하나씩 지워가는 뿌듯함으로 마지막까지 채워요."),
    }
