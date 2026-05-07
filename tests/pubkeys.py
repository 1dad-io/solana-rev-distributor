_BASE58_ALPHABET = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")


def make_test_pubkey(prefix: str, index: int, length: int = 32) -> str:
    if not prefix:
        raise ValueError("prefix must not be empty")

    if any(char not in _BASE58_ALPHABET for char in prefix):
        raise ValueError("prefix must contain only Base58 characters")

    if index < 1 or index > 9:
        raise ValueError("index must be between 1 and 9")

    if len(prefix) >= length:
        raise ValueError("prefix is too long for requested key length")

    digit = str(index)
    return prefix + digit * (length - len(prefix))


def make_validator_pubkey(index: int) -> str:
    return make_test_pubkey("Va1idator", index)


def make_staker_pubkey(index: int) -> str:
    return make_test_pubkey("Staker", index)


def make_vote_account_pubkey(index: int) -> str:
    return make_test_pubkey("VoteAcc", index)
