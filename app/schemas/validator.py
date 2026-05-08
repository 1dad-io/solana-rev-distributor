from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.demo import (
    DEMO_ALIAS_VALIDATOR,
    DEMO_VALIDATOR_IDENTITY,
    DEMO_VOTE_ACCOUNT,
)
from app.validators.pubkeys import (
    validate_validator_identity_pubkey,
    validate_vote_account_pubkey,
)


class ValidatorCreate(BaseModel):
    identity_pubkey: str = Field(
        min_length=32,
        max_length=64,
        description="Validator identity pubkey.",
        examples=[DEMO_VALIDATOR_IDENTITY],
    )
    vote_account_pubkey: str = Field(
        min_length=32,
        max_length=64,
        description="Validator vote account pubkey.",
        examples=[DEMO_VOTE_ACCOUNT],
    )
    alias: str = Field(
        min_length=1,
        max_length=128,
        description="Human-readable validator alias.",
        examples=[DEMO_ALIAS_VALIDATOR],
    )
    cluster: str = Field(
        min_length=1,
        max_length=32,
        description="Cluster name.",
        examples=["testnet"],
    )
    is_active: bool = Field(
        default=True,
        description="Whether the validator record is active.",
        examples=[True],
    )

    @field_validator("identity_pubkey", mode="before")
    @classmethod
    def normalize_identity_pubkey(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("vote_account_pubkey", mode="before")
    @classmethod
    def normalize_vote_account_pubkey(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value

    @field_validator("identity_pubkey")
    @classmethod
    def validate_identity_pubkey_field(cls, value: str) -> str:
        return validate_validator_identity_pubkey(value)

    @field_validator("vote_account_pubkey")
    @classmethod
    def validate_vote_account_pubkey_field(cls, value: str) -> str:
        return validate_vote_account_pubkey(value)


class ValidatorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Internal validator ID.", examples=[1])
    identity_pubkey: str = Field(
        description="Validator identity pubkey.",
        examples=[DEMO_VALIDATOR_IDENTITY],
    )
    vote_account_pubkey: str = Field(
        description="Validator vote account pubkey.",
        examples=[DEMO_VOTE_ACCOUNT],
    )
    alias: str = Field(description="Validator alias.", examples=[DEMO_ALIAS_VALIDATOR])
    cluster: str = Field(description="Cluster name.", examples=["testnet"])
    is_active: bool = Field(description="Whether the validator record is active.", examples=[True])
    created_at: datetime = Field(description="Creation timestamp.")
    updated_at: datetime = Field(description="Last update timestamp.")
