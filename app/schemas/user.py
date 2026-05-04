from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    role: Literal["validator", "staker"]
    alias: str | None = Field(default=None, max_length=128)
    validator_identity_pubkey: str | None = Field(default=None, min_length=32, max_length=64)
    staker_withdrawer_pubkey: str | None = Field(default=None, min_length=32, max_length=64)
    is_active: bool = True


class UserCreate(UserBase):
    password_hash: str = Field(min_length=1, max_length=255)

    @model_validator(mode="after")
    def validate_role_pubkeys(self) -> "UserCreate":
        if self.role == "validator" and not self.validator_identity_pubkey:
            raise ValueError("validator_identity_pubkey is required for validator role")
        if self.role == "staker" and not self.staker_withdrawer_pubkey:
            raise ValueError("staker_withdrawer_pubkey is required for staker role")
        return self


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ValidatorMeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    role: Literal["validator"]
    alias: str | None = None
    validator_identity_pubkey: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ValidatorMeUpdate(BaseModel):
    alias: str | None = Field(default=None, max_length=128)
    is_active: bool | None = None


class StakerMeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    role: Literal["staker"]
    alias: str | None = None
    staker_withdrawer_pubkey: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class StakerMeUpdate(BaseModel):
    alias: str | None = Field(default=None, max_length=128)
    is_active: bool | None = None
