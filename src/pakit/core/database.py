from sqlmodel import create_engine, Session, SQLModel
from pakit.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, connect_args={"connect_timeout": 10})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
