from tests.conftest import DEMO_VOTE_ACCOUNT
from tests.pubkeys import (
    make_staker_pubkey,
    make_validator_pubkey,
    make_vote_account_pubkey,
)


def test_signup_validator(client) -> None:
    payload = {
        "username": "validator1",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator User",
        "validator_identity_pubkey": make_validator_pubkey(3),
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }

    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "validator1"
    assert data["role"] == "validator"
    assert data["alias"] == "Validator User"
    assert data["validator_identity_pubkey"] == make_validator_pubkey(3)
    assert data["is_active"] is True


def test_signup_staker(client) -> None:
    payload = {
        "username": "staker1",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker User",
        "staker_withdrawer_pubkey": make_staker_pubkey(4),
        "is_active": True,
    }

    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "staker1"
    assert data["role"] == "staker"
    assert data["alias"] == "Staker User"
    assert data["staker_withdrawer_pubkey"] == make_staker_pubkey(4)
    assert data["is_active"] is True


def test_signup_duplicate_username_fails(client) -> None:
    payload = {
        "username": "duplicate_user",
        "password": "secret123",
        "role": "staker",
        "alias": "First User",
        "staker_withdrawer_pubkey": make_staker_pubkey(6),
        "is_active": True,
    }

    first_response = client.post("/auth/signup", json=payload)
    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/signup",
        json={
            "username": "duplicate_user",
            "password": "secret123",
            "role": "validator",
            "alias": "Second User",
            "validator_identity_pubkey": make_validator_pubkey(7),
            "vote_account_pubkey": make_vote_account_pubkey(8),
            "is_active": True,
        },
    )
    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "User or validator with the same username or public key already exists"
    )


def test_signup_duplicate_validator_identity_pubkey_fails(client) -> None:
    validator_identity_pubkey = make_validator_pubkey(1)

    first_response = client.post(
        "/auth/signup",
        json={
            "username": "duplicate_validator_a",
            "password": "secret123",
            "role": "validator",
            "alias": "Duplicate Validator A",
            "validator_identity_pubkey": validator_identity_pubkey,
            "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
            "is_active": True,
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/signup",
        json={
            "username": "duplicate_validator_b",
            "password": "secret123",
            "role": "validator",
            "alias": "Duplicate Validator B",
            "validator_identity_pubkey": validator_identity_pubkey,
            "vote_account_pubkey": make_vote_account_pubkey(2),
            "is_active": True,
        },
    )
    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "User or validator with the same username or public key already exists"
    )


def test_signup_duplicate_staker_withdrawer_pubkey_fails(client) -> None:
    staker_withdrawer_pubkey = make_staker_pubkey(9)

    first_response = client.post(
        "/auth/signup",
        json={
            "username": "duplicate_staker_a",
            "password": "secret123",
            "role": "staker",
            "alias": "Duplicate Staker A",
            "staker_withdrawer_pubkey": staker_withdrawer_pubkey,
            "is_active": True,
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/auth/signup",
        json={
            "username": "duplicate_staker_b",
            "password": "secret123",
            "role": "staker",
            "alias": "Duplicate Staker B",
            "staker_withdrawer_pubkey": staker_withdrawer_pubkey,
            "is_active": True,
        },
    )
    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "User or validator with the same username or public key already exists"
    )


def test_login_success(client) -> None:
    signup_payload = {
        "username": "validator2",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Two",
        "validator_identity_pubkey": make_validator_pubkey(5),
        "vote_account_pubkey": make_vote_account_pubkey(1),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    response = client.post(
        "/auth/login",
        data={"username": "validator2", "password": "secret123"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client) -> None:
    signup_payload = {
        "username": "validator3",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Three",
        "validator_identity_pubkey": make_validator_pubkey(8),
        "vote_account_pubkey": make_vote_account_pubkey(4),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    response = client.post(
        "/auth/login",
        data={"username": "validator3", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_login_unknown_user(client) -> None:
    response = client.post(
        "/auth/login",
        data={"username": "missing_user", "password": "secret123"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid username or password"


def test_auth_me_with_token(client) -> None:
    signup_payload = {
        "username": "staker2",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Two",
        "staker_withdrawer_pubkey": make_staker_pubkey(7),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker2", "password": "secret123"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "staker2"
    assert data["role"] == "staker"
    assert data["alias"] == "Staker Two"
    assert data["staker_withdrawer_pubkey"] == make_staker_pubkey(7)
    assert data["is_active"] is True


def test_auth_me_requires_authentication(client) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_auth_me_rejects_invalid_token(client) -> None:
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_inactive_staker_cannot_login(client) -> None:
    signup_payload = {
        "username": "staker_inactive_login",
        "password": "secret123",
        "role": "staker",
        "alias": "Inactive Staker",
        "staker_withdrawer_pubkey": make_staker_pubkey(1),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_inactive_login", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    deactivate_response = client.put(
        "/stakers/me",
        json={"alias": "Inactive Staker", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    second_login_response = client.post(
        "/auth/login",
        data={"username": "staker_inactive_login", "password": "secret123"},
    )
    assert second_login_response.status_code == 403
    assert second_login_response.json()["detail"] == "Inactive user"


def test_inactive_validator_cannot_login(client) -> None:
    signup_payload = {
        "username": "validator_inactive_login",
        "password": "secret123",
        "role": "validator",
        "alias": "Inactive Validator",
        "validator_identity_pubkey": make_validator_pubkey(1),
        "vote_account_pubkey": make_vote_account_pubkey(5),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_inactive_login", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    deactivate_response = client.put(
        "/validators/me",
        json={"alias": "Inactive Validator", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    second_login_response = client.post(
        "/auth/login",
        data={"username": "validator_inactive_login", "password": "secret123"},
    )
    assert second_login_response.status_code == 403
    assert second_login_response.json()["detail"] == "Inactive user"
