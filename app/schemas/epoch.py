from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EpochImportRequest(BaseModel):
    epoch: int = Field(ge=0)
    block_rewards_lamports: int = Field(ge=0)
    uptime_bps: int = Field(default=10000, ge=0, le=10000)


class EpochRewardContextRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    validator_identity_pubkey: str
    cluster: str
    epoch: int
    mev_revenue_lamports: int
    mev_commission_bps: int
    block_rewards_lamports: int
    uptime_bps: int
    source_path: str
    source_hash: str | None
    created_at: datetime
    updated_at: datetime
