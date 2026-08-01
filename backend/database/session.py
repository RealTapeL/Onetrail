from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings

database_url = get_settings().database_url
engine_options: dict = {"pool_pre_ping": True}
if database_url.startswith("sqlite"):
    # SQLite is used by automated tests only; this option is invalid for PostgreSQL.
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
