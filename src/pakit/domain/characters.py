from dataclasses import dataclass

from pakit.domain.assessment import MbtiType


@dataclass(frozen=True)
class Character:
    noun: str
    code: str
    asset_key: str


CHARACTERS: dict[MbtiType, Character] = {
    MbtiType.INTJ: Character("큐브", "cube", "characters/cube.png"),
    MbtiType.ISTJ: Character("로봇", "robot", "characters/robot.png"),
    MbtiType.ENTJ: Character("불도저", "bulldozer", "characters/bulldozer.png"),
    MbtiType.ESTJ: Character("헬리콥터", "helicopter", "characters/helicopter.png"),
    MbtiType.INFJ: Character("비밀상자", "secret_box", "characters/secret_box.png"),
    MbtiType.ISFJ: Character("테디베어", "teddy_bear", "characters/teddy_bear.png"),
    MbtiType.ENFJ: Character("기차", "train", "characters/train.png"),
    MbtiType.ESFJ: Character("티포트", "teapot", "characters/teapot.png"),
    MbtiType.INFP: Character("쿠크다스", "cookie", "characters/cookie.png"),
    MbtiType.ISFP: Character("침대", "bed", "characters/bed.png"),
    MbtiType.ENFP: Character("연", "kite", "characters/kite.png"),
    MbtiType.ESFP: Character("실로폰", "xylophone", "characters/xylophone.png"),
    MbtiType.INTP: Character("망원경", "telescope", "characters/telescope.png"),
    MbtiType.ISTP: Character("공구함", "toolbox", "characters/toolbox.png"),
    MbtiType.ENTP: Character("팽이", "spinning_top", "characters/spinning_top.png"),
    MbtiType.ESTP: Character("RC카", "rc_car", "characters/rc_car.png"),
}

NOUNS: dict[MbtiType, str] = {mbti: character.noun for mbti, character in CHARACTERS.items()}
