import base58

MIN_PUBKEY_LENGTH = 32
MAX_PUBKEY_LENGTH = 64


def validate_base58_pubkey(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")

    if len(normalized) < MIN_PUBKEY_LENGTH or len(normalized) > MAX_PUBKEY_LENGTH:
        raise ValueError(
            f"{field_name} must be between {MIN_PUBKEY_LENGTH} and "
            f"{MAX_PUBKEY_LENGTH} characters long"
        )

    try:
        base58.b58decode(normalized)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid Base58 public key") from exc

    return normalized


def validate_validator_identity_pubkey(value: str) -> str:
    return validate_base58_pubkey(value, "validator_identity_pubkey")


def validate_staker_withdrawer_pubkey(value: str) -> str:
    return validate_base58_pubkey(value, "staker_withdrawer_pubkey")


def validate_vote_account_pubkey(value: str) -> str:
    return validate_base58_pubkey(value, "vote_account_pubkey")
