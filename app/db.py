from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models import Base

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def ensure_runtime_dirs() -> None:
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.stakes_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.validator_rewards_dir).mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    ensure_runtime_dirs()
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
