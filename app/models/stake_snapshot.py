# pylint: disable=too-few-public-methods

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StakeSnapshot(Base):
    __tablename__ = "stake_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    validator_identity_pubkey: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    cluster: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    epoch: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    source_path: Mapped[str] = mapped_column(String(512), nullable=False)
    source_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    records_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
