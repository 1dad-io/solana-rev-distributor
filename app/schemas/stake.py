from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.examples import DEMO_EPOCH, DEMO_STAKE_ACCOUNT, DEMO_STAKER_WITHDRAWER, DEMO_VOTE_ACCOUNT


class StakeImportRequest(BaseModel):
    epoch: int | None = Field(
        default=None,
        ge=0,
        description="Stake snapshot epoch. If omitted, the default epoch is resolved automatically.",
        examples=[DEMO_EPOCH],
    )


class StakeSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Internal snapshot ID.", examples=[1])
    validator_identity_pubkey: str = Field(description="Validator identity pubkey.")
    cluster: str = Field(description="Cluster name.", examples=["testnet"])
    epoch: int = Field(description="Snapshot epoch.", examples=[DEMO_EPOCH])
    source_path: str = Field(description="Path to the imported source file.", examples=["data/testnet/stakes/0.json"])
    source_hash: str | None = Field(description="SHA-256 hash of the source file.")
    records_count: int = Field(description="Number of imported stake accounts.", examples=[1])
    imported_at: datetime = Field(description="Import timestamp.")


class StakeAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Internal stake account row ID.", examples=[1])
    snapshot_id: int = Field(description="Parent snapshot ID.", examples=[1])
    stake_pubkey: str = Field(description="Stake account pubkey.", examples=[DEMO_STAKE_ACCOUNT])
    stake_type: str | None = Field(description="Stake account type.", examples=["Stake"])
    account_balance_lamports: int | None = Field(description="Account balance in lamports.", examples=[14889939721])
    credits_observed: int | None = Field(description="Observed credits.", examples=[718890781])
    delegated_stake_lamports: int | None = Field(description="Delegated stake in lamports.", examples=[14887656841])
    active_stake_lamports: int | None = Field(description="Active stake in lamports.", examples=[14887656841])
    delegated_vote_account_pubkey: str | None = Field(
        description="Delegated validator vote account pubkey.",
        examples=[DEMO_VOTE_ACCOUNT],
    )
    activation_epoch: int | None = Field(description="Activation epoch.", examples=[686])
    deactivation_epoch: int | None = Field(description="Deactivation epoch.")
    staker_authority: str | None = Field(description="Staker authority pubkey.", examples=[DEMO_STAKER_WITHDRAWER])
    withdrawer_authority: str | None = Field(
        description="Withdrawer authority pubkey.",
        examples=[DEMO_STAKER_WITHDRAWER],
    )
    rent_exempt_reserve_lamports: int | None = Field(description="Rent exempt reserve in lamports.", examples=[2282880])
    created_at: datetime = Field(description="Creation timestamp.")
