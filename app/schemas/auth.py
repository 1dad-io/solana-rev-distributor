from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=3, max_length=255)
    role: Literal["validator", "staker"]
    alias: str | None = Field(default=None, max_length=128)
    validator_identity_pubkey: str | None = Field(default=None, min_length=32, max_length=64)
    staker_withdrawer_pubkey: str | None = Field(default=None, min_length=32, max_length=64)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_role_pubkeys(self) -> "SignupRequest":
        if self.role == "validator" and not self.validator_identity_pubkey:
            raise ValueError("validator_identity_pubkey is required for validator role")
        if self.role == "staker" and not self.staker_withdrawer_pubkey:
            raise ValueError("staker_withdrawer_pubkey is required for staker role")
        return self


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
