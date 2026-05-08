from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.demo import (
    DEMO_BLOCK_REWARDS_BPS_BACK,
    DEMO_MEV_BPS_BACK,
    DEMO_STAKER_WITHDRAWER,
    DEMO_VALIDATOR_IDENTITY,
)
from app.validators.pubkeys import validate_staker_withdrawer_pubkey


class RewardPolicyCreate(BaseModel):
    staker_withdrawer_pubkey: str | None = Field(
        default=None,
        min_length=32,
        max_length=64,
        description="Staker withdrawer pubkey. Leave empty only for a default policy.",
    )
    is_default: bool = Field(
        default=False,
        description="Whether this policy is the validator default policy.",
        examples=[False],
    )
    mev_bps_back: int = Field(
        ge=0,
        le=10000,
        description="MEV share returned to the staker in basis points.",
        examples=[DEMO_MEV_BPS_BACK],
    )
    block_rewards_bps_back: int = Field(
        ge=0,
        le=10000,
        description="Block rewards share returned to the staker in basis points.",
        examples=[DEMO_BLOCK_REWARDS_BPS_BACK],
    )
    valid_from_epoch: int | None = Field(
        default=None,
        ge=0,
        description="Optional lower bound epoch for this policy. Null means no lower limit.",
        examples=[None],
    )
    valid_to_epoch: int | None = Field(
        default=None,
        ge=0,
        description="Optional upper bound epoch for this policy. Null means no upper limit.",
        examples=[None],
    )
    is_active: bool = Field(
        default=True,
        description="Whether this policy is active.",
        examples=[True],
    )

    @field_validator("staker_withdrawer_pubkey", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value.strip() if isinstance(value, str) else value

    @field_validator("staker_withdrawer_pubkey")
    @classmethod
    def validate_staker_withdrawer_pubkey_field(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_staker_withdrawer_pubkey(value)

    @field_validator("valid_to_epoch")
    @classmethod
    def validate_epoch_range(cls, value: int | None, info) -> int | None:
        valid_from_epoch = info.data.get("valid_from_epoch")
        if value is not None and valid_from_epoch is not None and value < valid_from_epoch:
            raise ValueError("valid_to_epoch must be greater than or equal to valid_from_epoch")
        return value

    @model_validator(mode="after")
    def validate_default_policy_fields(self) -> "RewardPolicyCreate":
        if self.is_default and self.staker_withdrawer_pubkey is not None:
            raise ValueError("Default policy must not contain staker_withdrawer_pubkey")
        if not self.is_default and self.staker_withdrawer_pubkey is None:
            raise ValueError("Non-default policy requires staker_withdrawer_pubkey")
        return self


class RewardPolicyUpdate(BaseModel):
    staker_withdrawer_pubkey: str | None = Field(
        default=None,
        min_length=32,
        max_length=64,
        description="Staker withdrawer pubkey. Leave empty only for a default policy.",
    )
    is_default: bool = Field(
        default=False,
        description="Whether this policy is the validator default policy.",
        examples=[False],
    )
    mev_bps_back: int = Field(
        ge=0,
        le=10000,
        description="MEV share returned to the staker in basis points.",
        examples=[DEMO_MEV_BPS_BACK],
    )
    block_rewards_bps_back: int = Field(
        ge=0,
        le=10000,
        description="Block rewards share returned to the staker in basis points.",
        examples=[DEMO_BLOCK_REWARDS_BPS_BACK],
    )
    valid_from_epoch: int | None = Field(
        default=None,
        ge=0,
        description="Optional lower bound epoch for this policy. Null means no lower limit.",
        examples=[None],
    )
    valid_to_epoch: int | None = Field(
        default=None,
        ge=0,
        description="Optional upper bound epoch for this policy. Null means no upper limit.",
        examples=[None],
    )
    is_active: bool = Field(
        default=True,
        description="Whether this policy is active.",
        examples=[True],
    )

    @field_validator("staker_withdrawer_pubkey", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value.strip() if isinstance(value, str) else value

    @field_validator("staker_withdrawer_pubkey")
    @classmethod
    def validate_staker_withdrawer_pubkey_field(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_staker_withdrawer_pubkey(value)

    @field_validator("valid_to_epoch")
    @classmethod
    def validate_epoch_range(cls, value: int | None, info) -> int | None:
        valid_from_epoch = info.data.get("valid_from_epoch")
        if value is not None and valid_from_epoch is not None and value < valid_from_epoch:
            raise ValueError("valid_to_epoch must be greater than or equal to valid_from_epoch")
        return value

    @model_validator(mode="after")
    def validate_default_policy_fields(self) -> "RewardPolicyUpdate":
        if self.is_default and self.staker_withdrawer_pubkey is not None:
            raise ValueError("Default policy must not contain staker_withdrawer_pubkey")
        if not self.is_default and self.staker_withdrawer_pubkey is None:
            raise ValueError("Non-default policy requires staker_withdrawer_pubkey")
        return self


class RewardPolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Internal reward policy ID.", examples=[1])
    validator_identity_pubkey: str = Field(
        description="Validator identity pubkey.",
        examples=[DEMO_VALIDATOR_IDENTITY],
    )
    cluster: str = Field(description="Cluster name.", examples=["testnet"])
    staker_withdrawer_pubkey: str | None = Field(
        description="Staker withdrawer pubkey. Null for default policy.",
        examples=[DEMO_STAKER_WITHDRAWER],
    )
    is_default: bool = Field(description="Whether this is a default policy.", examples=[False])
    mev_bps_back: int = Field(
        description="MEV share returned in basis points.",
        examples=[DEMO_MEV_BPS_BACK],
    )
    block_rewards_bps_back: int = Field(
        description="Block rewards share returned in basis points.",
        examples=[DEMO_BLOCK_REWARDS_BPS_BACK],
    )
    valid_from_epoch: int | None = Field(
        description="Optional lower bound epoch. Null means no lower limit.",
        examples=[None],
    )
    valid_to_epoch: int | None = Field(
        description="Optional upper bound epoch. Null means no upper limit.",
        examples=[None],
    )
    is_active: bool = Field(description="Whether this policy is active.", examples=[True])
    created_at: datetime = Field(description="Creation timestamp.")
    updated_at: datetime = Field(description="Last update timestamp.")
