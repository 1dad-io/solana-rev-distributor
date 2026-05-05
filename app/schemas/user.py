from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.examples import (
    DEMO_ALIAS_STAKER,
    DEMO_ALIAS_VALIDATOR,
    DEMO_PASSWORD,
    DEMO_STAKER_WITHDRAWER,
    DEMO_USERNAME_STAKER,
    DEMO_USERNAME_VALIDATOR,
    DEMO_VALIDATOR_IDENTITY,
    DEMO_VOTE_ACCOUNT,
)


class UserCreate(BaseModel):
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
        examples=[DEMO_VALIDATOR_IDENTITY],
    )
    vote_account_pubkey: str | None = Field(
        default=None,
        min_length=32,
        max_length=64,
        description="Validator vote account pubkey. Required only for validator role.",
        examples=[DEMO_VOTE_ACCOUNT],
    )
    staker_withdrawer_pubkey: str | None = Field(
        default=None,
        min_length=32,
        max_length=64,
        description="Staker withdrawer pubkey. Required only for staker role.",
        examples=[DEMO_STAKER_WITHDRAWER],
    )
    is_active: bool = Field(
        default=True,
        description="Whether the user is active.",
        examples=[True],
    )

    @field_validator(
        "alias",
        "validator_identity_pubkey",
        "vote_account_pubkey",
        "staker_withdrawer_pubkey",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @model_validator(mode="after")
    def validate_role_fields(self) -> "UserCreate":
        if self.role == "validator":
            if not self.validator_identity_pubkey:
                raise ValueError("validator_identity_pubkey is required for validator role")
            if not self.vote_account_pubkey:
                raise ValueError("vote_account_pubkey is required for validator role")
            if self.staker_withdrawer_pubkey is not None:
                raise ValueError("staker_withdrawer_pubkey must be empty for validator role")

        if self.role == "staker":
            if not self.staker_withdrawer_pubkey:
                raise ValueError("staker_withdrawer_pubkey is required for staker role")
            if self.validator_identity_pubkey is not None:
                raise ValueError("validator_identity_pubkey must be empty for staker role")
            if self.vote_account_pubkey is not None:
                raise ValueError("vote_account_pubkey must be empty for staker role")

        return self


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Internal user ID.", examples=[1])
    username: str = Field(description="Application username.", examples=[DEMO_USERNAME_VALIDATOR])
    role: str = Field(description="User role.", examples=["validator"])
    alias: str | None = Field(description="Human-readable alias.", examples=[DEMO_ALIAS_VALIDATOR])
    validator_identity_pubkey: str | None = Field(
        description="Validator identity pubkey.",
        examples=[DEMO_VALIDATOR_IDENTITY],
    )
    staker_withdrawer_pubkey: str | None = Field(
        description="Staker withdrawer pubkey.",
        examples=[DEMO_STAKER_WITHDRAWER],
    )
    is_active: bool = Field(description="Whether the user is active.", examples=[True])


class ValidatorMeRead(BaseModel):
    username: str = Field(description="Validator username.", examples=[DEMO_USERNAME_VALIDATOR])
    role: str = Field(description="User role.", examples=["validator"])
    alias: str | None = Field(description="Validator alias.", examples=[DEMO_ALIAS_VALIDATOR])
    validator_identity_pubkey: str | None = Field(
        description="Validator identity pubkey.",
        examples=[DEMO_VALIDATOR_IDENTITY],
    )
    vote_account_pubkey: str | None = Field(
        description="Validator vote account pubkey.",
        examples=[DEMO_VOTE_ACCOUNT],
    )
    is_active: bool = Field(description="Whether the validator user is active.", examples=[True])


class ValidatorMeUpdate(BaseModel):
    alias: str | None = Field(
        default=None,
        max_length=128,
        description="New validator alias.",
        examples=[DEMO_ALIAS_VALIDATOR],
    )
    is_active: bool | None = Field(
        default=None,
        description="Updated active flag.",
        examples=[True],
    )

    @field_validator("alias", mode="before")
    @classmethod
    def empty_alias_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value


class StakerMeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str = Field(description="Staker username.", examples=[DEMO_USERNAME_STAKER])
    role: str = Field(description="User role.", examples=["staker"])
    alias: str | None = Field(description="Staker alias.", examples=[DEMO_ALIAS_STAKER])
    staker_withdrawer_pubkey: str | None = Field(
        description="Staker withdrawer pubkey.",
        examples=[DEMO_STAKER_WITHDRAWER],
    )
    is_active: bool = Field(description="Whether the staker user is active.", examples=[True])


class StakerMeUpdate(BaseModel):
    alias: str | None = Field(
        default=None,
        max_length=128,
        description="New staker alias.",
        examples=[DEMO_ALIAS_STAKER],
    )
    is_active: bool | None = Field(
        default=None,
        description="Updated active flag.",
        examples=[True],
    )

    @field_validator("alias", mode="before")
    @classmethod
    def empty_alias_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value
