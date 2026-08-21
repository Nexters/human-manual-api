from pydantic import SecretStr

from pakit.core.config import Settings


def test_builds_an_async_postgres_url_and_escapes_credentials() -> None:
    settings = Settings(
        database_host="db",
        database_port=5432,
        database_name="pakit",
        database_user="pakit@example.com",
        database_password=SecretStr("p@ss/word"),
    )

    assert settings.database_url == (
        "postgresql+asyncpg://pakit%40example.com:p%40ss%2Fword@db:5432/pakit"
    )


def test_admin_and_usage_tracking_are_disabled_by_default() -> None:
    settings = Settings(_env_file=None)

    assert settings.admin_username is None
    assert settings.admin_password is None
    assert settings.usage_tracking_started_at is None
