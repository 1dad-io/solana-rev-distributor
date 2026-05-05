from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.examples import (
    DEMO_BLOCK_REWARDS_LAMPORTS,
    DEMO_EPOCH,
    DEMO_MEV_REVENUE_LAMPORTS,
    DEMO_UPTIME_BPS,
)


class EpochImportRequest(BaseModel):
    epoch: int | None = Field(
        default=None,
        ge=0,
        description="Reward context epoch. If omitted, the default epoch is resolved automatically.",
        examples=[DEMO_EPOCH],
    )
    block_rewards_lamports: int = Field(
        ge=0,
        description="Block rewards for the epoch in lamports.",
        examples=[DEMO_BLOCK_REWARDS_LAMPORTS],
    )
    uptime_bps: int = Field(
        default=10000,
        ge=0,
        le=10000,
        description="Validator uptime in basis points.",
        examples=[DEMO_UPTIME_BPS],
    )


class EpochRewardContextRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Internal epoch reward context ID.", examples=[1])
    validator_identity_pubkey: str = Field(description="Validator identity pubkey.")
    cluster: str = Field(description="Cluster name.", examples=["testnet"])
    epoch: int = Field(description="Epoch number.", examples=[DEMO_EPOCH])
    mev_revenue_lamports: int = Field(
        description="MEV revenue in lamports.",
        examples=[DEMO_MEV_REVENUE_LAMPORTS],
    )
    mev_commission_bps: int = Field(description="MEV commission in basis points.", examples=[10000])
    block_rewards_lamports: int = Field(
        description="Block rewards in lamports.",
        examples=[DEMO_BLOCK_REWARDS_LAMPORTS],
    )
    uptime_bps: int = Field(description="Validator uptime in basis points.", examples=[DEMO_UPTIME_BPS])
    source_path: str = Field(
        description="Path to the imported source file.",
        examples=["data/testnet/validator_rewards/0.json"],
    )
    source_hash: str | None = Field(description="SHA-256 hash of the source file.")
    created_at: datetime = Field(description="Creation timestamp.")
    updated_at: datetime = Field(description="Last update timestamp.")
