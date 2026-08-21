import pytest

from pakit.api.schemas.image_urls import absolute_image_url


@pytest.mark.parametrize(
    ("path", "public_base_url", "expected"),
    [
        (
            "/assets/characters/telescope.png",
            "http://api.pakit.kr/",
            "https://api.pakit.kr/assets/characters/telescope.png",
        ),
        (
            "http://cdn.pakit.kr/characters/telescope.png",
            "http://api.pakit.kr/",
            "https://cdn.pakit.kr/characters/telescope.png",
        ),
        (
            "/assets/characters/telescope.png",
            "http://localhost:8000/",
            "http://localhost:8000/assets/characters/telescope.png",
        ),
        (
            "/assets/characters/telescope.png",
            "https://api.pakit.kr/",
            "https://api.pakit.kr/assets/characters/telescope.png",
        ),
    ],
)
def test_builds_secure_absolute_image_urls(path: str, public_base_url: str, expected: str) -> None:
    assert absolute_image_url(path, public_base_url=public_base_url) == expected
