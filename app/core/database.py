from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)


def get_session():
    """FastAPI dependency that yields a DB session and closes it afterwards."""
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    """Used only for quick local testing; real schema changes go through Alembic."""
    SQLModel.metadata.create_all(engine)
