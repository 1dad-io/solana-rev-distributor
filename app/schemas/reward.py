from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.examples import (
    DEMO_BLOCK_REWARDS_BPS_BACK,
    DEMO_EPOCH,
    DEMO_MEV_BPS_BACK,
    DEMO_STAKE_ACCOUNT,
    DEMO_STAKER_WITHDRAWER,
)


class RewardCalculationRequest(BaseModel):
    epoch: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Reward calculation epoch. "
            "If omitted, the default epoch is resolved automatically."
        ),
        examples=[DEMO_EPOCH],
    )
    force_recalculate: bool = Field(
        default=False,
        description="Whether to delete and rebuild existing rewards for the epoch.",
        examples=[True],
    )


class RewardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Internal reward row ID.", examples=[1])
    validator_identity_pubkey: str = Field(description="Validator identity pubkey.")
    cluster: str = Field(description="Cluster name.", examples=["testnet"])
    epoch: int = Field(description="Reward epoch.", examples=[DEMO_EPOCH])
    stake_account_id: int = Field(description="Imported stake account row ID.", examples=[1])
    policy_id_used: int | None = Field(description="Applied reward policy ID.", examples=[1])
    staker_withdrawer_pubkey: str = Field(
        description="Staker withdrawer pubkey.",
        examples=[DEMO_STAKER_WITHDRAWER],
    )
    stake_pubkey: str = Field(
        description="Stake account pubkey.",
        examples=[DEMO_STAKE_ACCOUNT],
    )
    withdrawer_authority: str = Field(
        description="Withdrawer authority pubkey.",
        examples=[DEMO_STAKER_WITHDRAWER],
    )
    active_stake_lamports: int = Field(
        description="Active stake in lamports.",
        examples=[14887656841],
    )
    validator_total_active_stake_lamports: int = Field(
        description="Validator total active stake in lamports for the epoch.",
        examples=[14887656841],
    )
    mev_bps_back_used: int | None = Field(
        description="Applied MEV share in basis points.",
        examples=[DEMO_MEV_BPS_BACK],
    )
    block_rewards_bps_back_used: int | None = Field(
        description="Applied block rewards share in basis points.",
        examples=[DEMO_BLOCK_REWARDS_BPS_BACK],
    )
    gross_mev_reward_lamports: int = Field(
        description="Calculated MEV reward in lamports.",
        examples=[500000000],
    )
    gross_block_reward_lamports: int = Field(
        description="Calculated block reward in lamports.",
        examples=[500000000],
    )
    gross_reward_lamports: int = Field(
        description="Gross reward in lamports.",
        examples=[1000000000],
    )
    payable_reward_lamports: int = Field(
        description="Payable reward in lamports.",
        examples=[1000000000],
    )
    status: str = Field(
        description="Reward calculation status.",
        examples=["calculated"],
    )
    calculated_at: datetime = Field(description="Calculation timestamp.")


class StakerStatsRead(BaseModel):
    staker_withdrawer_pubkey: str = Field(
        description="Staker withdrawer pubkey.",
        examples=[DEMO_STAKER_WITHDRAWER],
    )
    rewards_count: int = Field(
        description="Number of rewards in the result set.",
        examples=[1],
    )
    epochs_count: int = Field(
        description="Number of distinct epochs in the result set.",
        examples=[1],
    )
    stake_accounts_count: int = Field(
        description="Number of distinct stake accounts in the result set.",
        examples=[1],
    )
    gross_total_lamports: int = Field(
        description="Gross total rewards in lamports.",
        examples=[1000000000],
    )
    payable_total_lamports: int = Field(
        description="Payable total rewards in lamports.",
        examples=[1000000000],
    )
