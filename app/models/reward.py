# pylint: disable=too-few-public-methods

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Reward(Base):
    __tablename__ = "rewards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    validator_identity_pubkey: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    cluster: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    epoch: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    stake_account_id: Mapped[int] = mapped_column(
        ForeignKey("stake_accounts.id"), nullable=False, index=True
    )
    policy_id_used: Mapped[int | None] = mapped_column(
        ForeignKey("reward_policies.id"), nullable=True
    )

    staker_withdrawer_pubkey: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    stake_pubkey: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    withdrawer_authority: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )

    active_stake_lamports: Mapped[int] = mapped_column(Integer, nullable=False)
    validator_total_active_stake_lamports: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    mev_bps_back_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    block_rewards_bps_back_used: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    gross_mev_reward_lamports: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    gross_block_reward_lamports: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    gross_reward_lamports: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    payable_reward_lamports: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    status: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
