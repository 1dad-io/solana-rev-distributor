def test_validator_me_requires_auth(client) -> None:
    response = client.get("/validators/me")
    assert response.status_code == 401


def test_staker_me_requires_auth(client) -> None:
    response = client.get("/stakers/me")
    assert response.status_code == 401


def test_validator_can_get_own_profile(client) -> None:
    signup_payload = {
        "username": "validator_profile",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Profile",
        "validator_identity_pubkey": "99999999999999999999999999999999",
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
    assert data["validator_identity_pubkey"] == "99999999999999999999999999999999"


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
    assert data["staker_withdrawer_pubkey"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def test_staker_cannot_access_validator_me(client) -> None:
    signup_payload = {
        "username": "staker_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Forbidden",
        "staker_withdrawer_pubkey": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
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
