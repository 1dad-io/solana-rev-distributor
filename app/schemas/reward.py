from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RewardCalculationRequest(BaseModel):
    epoch: int = Field(ge=0)
    force_recalculate: bool = False


class RewardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    validator_identity_pubkey: str
    cluster: str
    epoch: int
    stake_account_id: int
    policy_id_used: int | None
    staker_withdrawer_pubkey: str
    stake_pubkey: str
    withdrawer_authority: str
    active_stake_lamports: int
    validator_total_active_stake_lamports: int
    mev_bps_back_used: int | None
    block_rewards_bps_back_used: int | None
    gross_mev_reward_lamports: int
    gross_block_reward_lamports: int
    gross_reward_lamports: int
    payable_reward_lamports: int
    status: str
    calculated_at: datetime


class StakerStatsRead(BaseModel):
    staker_withdrawer_pubkey: str
    rewards_count: int
    epochs_count: int
    stake_accounts_count: int
    gross_total_lamports: int
    payable_total_lamports: int
