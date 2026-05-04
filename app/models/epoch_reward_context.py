from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EpochRewardContext(Base):
    __tablename__ = "epoch_reward_contexts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    validator_identity_pubkey: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    cluster: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    epoch: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    mev_revenue_lamports: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mev_commission_bps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    block_rewards_lamports: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    uptime_bps: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)

    source_path: Mapped[str] = mapped_column(String(512), nullable=False)
    source_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

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
