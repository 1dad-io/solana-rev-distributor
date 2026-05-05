from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    role: Literal["validator", "staker"]
    alias: str | None = Field(default=None, max_length=128)
    validator_identity_pubkey: str | None = Field(default=None, min_length=32, max_length=64)
    staker_withdrawer_pubkey: str | None = Field(default=None, min_length=32, max_length=64)
    is_active: bool = True

    @field_validator(
        "alias",
        "validator_identity_pubkey",
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
            if self.staker_withdrawer_pubkey is not None:
                raise ValueError("staker_withdrawer_pubkey must be empty for validator role")

        if self.role == "staker":
            if not self.staker_withdrawer_pubkey:
                raise ValueError("staker_withdrawer_pubkey is required for staker role")
            if self.validator_identity_pubkey is not None:
                raise ValueError("validator_identity_pubkey must be empty for staker role")

        return self


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    alias: str | None
    validator_identity_pubkey: str | None
    staker_withdrawer_pubkey: str | None
    is_active: bool


class ValidatorMeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    role: str
    alias: str | None
    validator_identity_pubkey: str | None
    is_active: bool


class ValidatorMeUpdate(BaseModel):
    alias: str | None = Field(default=None, max_length=128)
    is_active: bool | None = None

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

    username: str
    role: str
    alias: str | None
    staker_withdrawer_pubkey: str | None
    is_active: bool


class StakerMeUpdate(BaseModel):
    alias: str | None = Field(default=None, max_length=128)
    is_active: bool | None = None

    @field_validator("alias", mode="before")
    @classmethod
    def empty_alias_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value
