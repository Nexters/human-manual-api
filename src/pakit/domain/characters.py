from dataclasses import dataclass

from pakit.domain.assessment import MbtiType


@dataclass(frozen=True)
class Character:
    noun: str
    code: str
    asset_key: str


CHARACTERS: dict[MbtiType, Character] = {
    MbtiType.INTJ: Character("큐브", "cube", "image_cube_340"),
    MbtiType.ISTJ: Character("로봇", "robot", "image_robot_340"),
    MbtiType.ENTJ: Character("불도저", "bulldozer", "image_bulldozer_340"),
    MbtiType.ESTJ: Character("헬리콥터", "helicopter", "image_helicopter_340"),
    MbtiType.INFJ: Character("비밀상자", "secret_box", "image_Secret_340"),
    MbtiType.ISFJ: Character("테디베어", "teddy_bear", "image_teddy bear_340"),
    MbtiType.ENFJ: Character("기차", "train", "image_train_340"),
    MbtiType.ESFJ: Character("티포트", "teapot", "image_tea_340"),
    MbtiType.INFP: Character("쿠크다스", "cookie", "image_쿠크다스_340"),
    MbtiType.ISFP: Character("침대", "bed", "image_bed_340"),
    MbtiType.ENFP: Character("연", "kite", "image_kite_340"),
    MbtiType.ESFP: Character("실로폰", "xylophone", "image_Xylophone_340"),
    MbtiType.INTP: Character("망원경", "telescope", "image_telescope_340"),
    MbtiType.ISTP: Character("공구함", "toolbox", "image_Tools_340"),
    MbtiType.ENTP: Character("팽이", "spinning_top", "image_top_340"),
    MbtiType.ESTP: Character("RC카", "rc_car", "image_rc카_340"),
}

NOUNS: dict[MbtiType, str] = {mbti: character.noun for mbti, character in CHARACTERS.items()}
