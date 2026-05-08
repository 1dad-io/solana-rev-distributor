from typing import Literal

from pydantic import field_validator, model_validator

from app.validators.pubkeys import (
    validate_staker_withdrawer_pubkey,
    validate_validator_identity_pubkey,
    validate_vote_account_pubkey,
)


class UserIdentityValidationMixin:
    role: Literal["validator", "staker"]
    validator_identity_pubkey: str | None
    vote_account_pubkey: str | None
    staker_withdrawer_pubkey: str | None

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
        return value.strip() if isinstance(value, str) else value

    @field_validator("validator_identity_pubkey")
    @classmethod
    def validate_validator_identity_pubkey_field(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_validator_identity_pubkey(value)

    @field_validator("vote_account_pubkey")
    @classmethod
    def validate_vote_account_pubkey_field(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_vote_account_pubkey(value)

    @field_validator("staker_withdrawer_pubkey")
    @classmethod
    def validate_staker_withdrawer_pubkey_field(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return validate_staker_withdrawer_pubkey(value)

    @model_validator(mode="after")
    def validate_role_fields(self):
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
