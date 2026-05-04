from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.base import Base

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def ensure_data_dirs() -> None:
    for directory in (
        settings.data_dir,
        settings.stakes_dir,
        settings.validator_rewards_dir,
    ):
        Path(directory).mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    ensure_data_dirs()
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
