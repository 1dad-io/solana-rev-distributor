from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StakeAccount(Base):
    __tablename__ = "stake_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    snapshot_id: Mapped[int] = mapped_column(ForeignKey("stake_snapshots.id"), nullable=False, index=True)

    stake_pubkey: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    stake_type: Mapped[str | None] = mapped_column(String(64), nullable=True)

    account_balance_lamports: Mapped[int | None] = mapped_column(Integer, nullable=True)
    credits_observed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delegated_stake_lamports: Mapped[int | None] = mapped_column(Integer, nullable=True)
    active_stake_lamports: Mapped[int | None] = mapped_column(Integer, nullable=True)

    delegated_vote_account_pubkey: Mapped[str | None] = mapped_column(String(64), nullable=True)

    activation_epoch: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deactivation_epoch: Mapped[int | None] = mapped_column(Integer, nullable=True)

    staker_authority: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    withdrawer_authority: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    rent_exempt_reserve_lamports: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
