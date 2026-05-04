from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RewardPolicyBase(BaseModel):
    staker_withdrawer_pubkey: str | None = Field(default=None, min_length=32, max_length=64)
    is_default: bool = False
    mev_bps_back: int = Field(ge=0, le=10000)
    block_rewards_bps_back: int = Field(ge=0, le=10000)
    valid_from_epoch: int | None = Field(default=None, ge=0)
    valid_to_epoch: int | None = Field(default=None, ge=0)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_policy_scope(self) -> "RewardPolicyBase":
        if self.is_default and self.staker_withdrawer_pubkey is not None:
            raise ValueError("Default policy must not contain staker_withdrawer_pubkey")
        if not self.is_default and self.staker_withdrawer_pubkey is None:
            raise ValueError("Non-default policy requires staker_withdrawer_pubkey")
        if (
            self.valid_from_epoch is not None
            and self.valid_to_epoch is not None
            and self.valid_from_epoch > self.valid_to_epoch
        ):
            raise ValueError("valid_from_epoch must be less than or equal to valid_to_epoch")
        return self


class RewardPolicyCreate(RewardPolicyBase):
    pass


class RewardPolicyRead(RewardPolicyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    validator_identity_pubkey: str
    cluster: str
    created_at: datetime
    updated_at: datetime
