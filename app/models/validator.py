# pylint: disable=too-few-public-methods

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Validator(Base):
    __tablename__ = "validators"
    __table_args__ = (
        UniqueConstraint("cluster", "identity_pubkey", name="uq_validators_cluster_identity"),
        UniqueConstraint("cluster", "vote_account_pubkey", name="uq_validators_cluster_vote"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    identity_pubkey: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    vote_account_pubkey: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    alias: Mapped[str] = mapped_column(String(128), nullable=False)
    cluster: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
