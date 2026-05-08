from tests.conftest import DEMO_VOTE_ACCOUNT
from tests.pubkeys import make_staker_pubkey, make_validator_pubkey


def test_signup_rejects_validator_identity_pubkey_with_invalid_zero_symbol(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_validator_key_zero",
            "password": "secret123",
            "role": "validator",
            "alias": "Invalid Validator Key Zero",
            "validator_identity_pubkey": "Va1idator000000000000000000000000",
            "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_validator_identity_pubkey_with_invalid_upper_o_symbol(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_validator_key_o",
            "password": "secret123",
            "role": "validator",
            "alias": "Invalid Validator Key O",
            "validator_identity_pubkey": "Va1idatOr111111111111111111111111",
            "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_validator_identity_pubkey_that_is_too_short(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_validator_key_short",
            "password": "secret123",
            "role": "validator",
            "alias": "Invalid Validator Key Short",
            "validator_identity_pubkey": "Va1idator1111111111111111111",
            "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_validator_identity_pubkey_that_is_too_long(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_validator_key_long",
            "password": "secret123",
            "role": "validator",
            "alias": "Invalid Validator Key Long",
            "validator_identity_pubkey": (
                "Va1idator11111111111111111111111111111111111111111111111111111111"
            ),
            "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_empty_validator_identity_pubkey(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_validator_key_empty",
            "password": "secret123",
            "role": "validator",
            "alias": "Invalid Validator Key Empty",
            "validator_identity_pubkey": "",
            "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_staker_withdrawer_pubkey_with_invalid_zero_symbol(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_staker_key_zero",
            "password": "secret123",
            "role": "staker",
            "alias": "Invalid Staker Key Zero",
            "staker_withdrawer_pubkey": "Staker00000000000000000000000000",
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_staker_withdrawer_pubkey_with_invalid_upper_i_symbol(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_staker_key_i",
            "password": "secret123",
            "role": "staker",
            "alias": "Invalid Staker Key I",
            "staker_withdrawer_pubkey": "StakerIIIIIIIIIIIIIIIIIIIIIIIIII",
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_staker_withdrawer_pubkey_that_is_too_short(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_staker_key_short",
            "password": "secret123",
            "role": "staker",
            "alias": "Invalid Staker Key Short",
            "staker_withdrawer_pubkey": "Staker111111111111111111111111",
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_staker_withdrawer_pubkey_that_is_too_long(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_staker_key_long",
            "password": "secret123",
            "role": "staker",
            "alias": "Invalid Staker Key Long",
            "staker_withdrawer_pubkey": (
                "Staker1111111111111111111111111111111111111111111111111111111111111111"
            ),
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_empty_staker_withdrawer_pubkey(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_staker_key_empty",
            "password": "secret123",
            "role": "staker",
            "alias": "Invalid Staker Key Empty",
            "staker_withdrawer_pubkey": "",
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_vote_account_pubkey_with_invalid_zero_symbol(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_vote_key_zero",
            "password": "secret123",
            "role": "validator",
            "alias": "Invalid Vote Key Zero",
            "validator_identity_pubkey": make_validator_pubkey(1),
            "vote_account_pubkey": "VoteAcc00000000000000000000000000",
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_vote_account_pubkey_with_invalid_lower_l_symbol(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_vote_key_l",
            "password": "secret123",
            "role": "validator",
            "alias": "Invalid Vote Key l",
            "validator_identity_pubkey": make_validator_pubkey(2),
            "vote_account_pubkey": "VoteAccllllllllllllllllllllllllll",
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_vote_account_pubkey_that_is_too_short(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_vote_key_short",
            "password": "secret123",
            "role": "validator",
            "alias": "Invalid Vote Key Short",
            "validator_identity_pubkey": make_validator_pubkey(3),
            "vote_account_pubkey": "VoteAcc111111111111111111111111",
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_vote_account_pubkey_that_is_too_long(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_vote_key_long",
            "password": "secret123",
            "role": "validator",
            "alias": "Invalid Vote Key Long",
            "validator_identity_pubkey": make_validator_pubkey(4),
            "vote_account_pubkey": (
                "VoteAcc1111111111111111111111111111111111111111111111111111111111"
            ),
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_signup_rejects_empty_vote_account_pubkey(client) -> None:
    response = client.post(
        "/auth/signup",
        json={
            "username": "invalid_vote_key_empty",
            "password": "secret123",
            "role": "validator",
            "alias": "Invalid Vote Key Empty",
            "validator_identity_pubkey": make_validator_pubkey(5),
            "vote_account_pubkey": "",
            "is_active": True,
        },
    )

    assert response.status_code == 422


def test_policy_create_rejects_invalid_staker_withdrawer_pubkey(client) -> None:
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": "policy_invalid_staker_key",
            "password": "secret123",
            "role": "validator",
            "alias": "Policy Invalid Staker Key",
            "validator_identity_pubkey": make_validator_pubkey(6),
            "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
            "is_active": True,
        },
    )
    assert signup_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={"username": "policy_invalid_staker_key", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": "Staker00000000000000000000000000",
            "is_default": False,
            "mev_bps_back": 5000,
            "block_rewards_bps_back": 2500,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_policy_update_rejects_invalid_staker_withdrawer_pubkey(client) -> None:
    signup_response = client.post(
        "/auth/signup",
        json={
            "username": "policy_invalid_staker_key_update",
            "password": "secret123",
            "role": "validator",
            "alias": "Policy Invalid Staker Key Update",
            "validator_identity_pubkey": make_validator_pubkey(7),
            "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
            "is_active": True,
        },
    )
    assert signup_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={"username": "policy_invalid_staker_key_update", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    create_response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": make_staker_pubkey(1),
            "is_default": False,
            "mev_bps_back": 5000,
            "block_rewards_bps_back": 2500,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 201
    policy_id = create_response.json()["id"]

    update_response = client.put(
        f"/validators/me/policies/{policy_id}",
        json={
            "staker_withdrawer_pubkey": "Staker00000000000000000000000000",
            "is_default": False,
            "mev_bps_back": 6000,
            "block_rewards_bps_back": 3000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert update_response.status_code == 422
