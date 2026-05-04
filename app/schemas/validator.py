from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ValidatorBase(BaseModel):
    identity_pubkey: str = Field(min_length=32, max_length=64)
    vote_account_pubkey: str = Field(min_length=32, max_length=64)
    alias: str = Field(min_length=1, max_length=128)
    cluster: Literal["testnet", "mainnet"]
    is_active: bool = True


class ValidatorCreate(ValidatorBase):
    pass


class ValidatorRead(ValidatorBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime
