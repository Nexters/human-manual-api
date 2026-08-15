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
        assert len(feature.description) <= 50


def test_builds_confirmed_curiosity_copy_for_entp() -> None:
    feature = build_motivation_feature("curiosity", MbtiType.ENTP)

    assert feature.title == "궁금하면 직진"
    assert feature.description == (
        "궁금한 건 검색만으로 넘기지 않고, 원리와 다른 가능성까지 직접 확인해요."
    )


def test_builds_concise_connected_fun_copy_for_entp() -> None:
    feature = build_motivation_feature("fun", MbtiType.ENTP)

    assert feature.description == (
        "재밌는 일이 시작되면 구경만 하지 않고, 더 재밌게 만들 방법까지 보태요."
    )
    assert len(feature.description) <= 50
