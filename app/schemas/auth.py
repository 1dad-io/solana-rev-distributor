from typing import Literal

from pydantic import BaseModel, Field

from app.demo import (
    DEMO_ALIAS_VALIDATOR,
    DEMO_PASSWORD,
    DEMO_USERNAME_VALIDATOR,
)
from app.schemas.user_identity import UserIdentityValidationMixin


class SignupRequest(UserIdentityValidationMixin, BaseModel):
    username: str = Field(
        min_length=3,
        max_length=64,
        description="Application username.",
        examples=[DEMO_USERNAME_VALIDATOR],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Application password.",
        examples=[DEMO_PASSWORD],
    )
    role: Literal["validator", "staker"] = Field(
        description="User role.",
        examples=["validator"],
    )
    alias: str | None = Field(
        default=None,
        max_length=128,
        description="Optional human-readable alias.",
        examples=[DEMO_ALIAS_VALIDATOR],
    )
    validator_identity_pubkey: str | None = Field(
        default=None,
        min_length=32,
        max_length=64,
        description="Validator identity pubkey. Required only for validator role.",
    )
    vote_account_pubkey: str | None = Field(
        default=None,
        min_length=32,
        max_length=64,
        description="Validator vote account pubkey. Required only for validator role.",
    )
    staker_withdrawer_pubkey: str | None = Field(
        default=None,
        min_length=32,
        max_length=64,
        description="Staker withdrawer pubkey. Required only for staker role.",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user is active.",
        examples=[True],
    )


class TokenResponse(BaseModel):
    access_token: str = Field(
        description="Bearer access token.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.demo.signature"],
    )
    token_type: str = Field(
        default="bearer",
        description="Token type.",
        examples=["bearer"],
    )
