from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StakeImportRequest(BaseModel):
    epoch: int = Field(ge=0)


class StakeSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    validator_identity_pubkey: str
    cluster: str
    epoch: int
    source_path: str
    source_hash: str | None
    records_count: int
    imported_at: datetime


class StakeAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    snapshot_id: int
    stake_pubkey: str
    stake_type: str | None
    account_balance_lamports: int | None
    credits_observed: int | None
    delegated_stake_lamports: int | None
    active_stake_lamports: int | None
    delegated_vote_account_pubkey: str | None
    activation_epoch: int | None
    deactivation_epoch: int | None
    staker_authority: str | None
    withdrawer_authority: str | None
    rent_exempt_reserve_lamports: int | None
    created_at: datetime
