from typing import Literal

from pydantic import BaseModel, Field, model_validator, field_validator


class SignupRequest(BaseModel):
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
    def validate_role_fields(self) -> "SignupRequest":
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


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
