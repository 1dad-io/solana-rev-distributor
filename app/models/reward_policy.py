from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RewardPolicy(Base):
    __tablename__ = "reward_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    validator_identity_pubkey: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    cluster: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    staker_withdrawer_pubkey: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    mev_bps_back: Mapped[int] = mapped_column(Integer, nullable=False)
    block_rewards_bps_back: Mapped[int] = mapped_column(Integer, nullable=False)

    valid_from_epoch: Mapped[int | None] = mapped_column(Integer, nullable=True)
    valid_to_epoch: Mapped[int | None] = mapped_column(Integer, nullable=True)

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
