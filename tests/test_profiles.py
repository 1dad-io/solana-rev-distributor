from tests.conftest import DEMO_VOTE_ACCOUNT


def test_staker_can_get_own_profile(client) -> None:
    signup_payload = {
        "username": "staker_profile",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Profile",
        "staker_withdrawer_pubkey": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_profile", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/stakers/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "staker_profile"
    assert data["role"] == "staker"
    assert data["alias"] == "Staker Profile"
    assert data["staker_withdrawer_pubkey"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    assert data["is_active"] is True


def test_validator_can_get_own_profile(client) -> None:
    signup_payload = {
        "username": "validator_profile",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Profile",
        "validator_identity_pubkey": "99999999999999999999999999999999",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_profile", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/validators/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "validator_profile"
    assert data["role"] == "validator"
    assert data["alias"] == "Validator Profile"
    assert data["validator_identity_pubkey"] == "99999999999999999999999999999999"
    assert data["vote_account_pubkey"] == DEMO_VOTE_ACCOUNT
    assert data["is_active"] is True


def test_staker_can_update_own_profile(client) -> None:
    signup_payload = {
        "username": "staker_update",
        "password": "secret123",
        "role": "staker",
        "alias": "Old Alias",
        "staker_withdrawer_pubkey": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_update", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.put(
        "/stakers/me",
        json={"alias": "New Alias", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["alias"] == "New Alias"
    assert data["is_active"] is False


def test_validator_can_update_own_profile(client) -> None:
    signup_payload = {
        "username": "validator_update",
        "password": "secret123",
        "role": "validator",
        "alias": "Old Validator Alias",
        "validator_identity_pubkey": "aaaaaaaa111111111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_update", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.put(
        "/validators/me",
        json={"alias": "New Validator Alias", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["alias"] == "New Validator Alias"
    assert data["vote_account_pubkey"] == DEMO_VOTE_ACCOUNT
    assert data["is_active"] is False


def test_staker_cannot_access_validator_me(client) -> None:
    signup_payload = {
        "username": "staker_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Forbidden",
        "staker_withdrawer_pubkey": "dddddddddddddddddddddddddddddddd",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/validators/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_validator_cannot_access_staker_me(client) -> None:
    signup_payload = {
        "username": "validator_forbidden",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Forbidden",
        "validator_identity_pubkey": "cccccccccccccccccccccccccccccccc",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/stakers/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
