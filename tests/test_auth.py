def test_signup_validator(client) -> None:
    payload = {
        "username": "validator1",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator User",
        "validator_identity_pubkey": "33333333333333333333333333333333",
        "is_active": True,
    }

    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == payload["username"]
    assert data["role"] == payload["role"]
    assert data["validator_identity_pubkey"] == payload["validator_identity_pubkey"]
    assert "password_hash" not in data


def test_signup_staker(client) -> None:
    payload = {
        "username": "staker1",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker User",
        "staker_withdrawer_pubkey": "44444444444444444444444444444444",
        "is_active": True,
    }

    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == payload["username"]
    assert data["role"] == payload["role"]
    assert data["staker_withdrawer_pubkey"] == payload["staker_withdrawer_pubkey"]
    assert "password_hash" not in data


def test_login_success(client) -> None:
    signup_payload = {
        "username": "validator2",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Two",
        "validator_identity_pubkey": "55555555555555555555555555555555",
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
        "validator_identity_pubkey": "66666666666666666666666666666666",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    response = client.post(
        "/auth/login",
        data={"username": "validator3", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_auth_me_with_token(client) -> None:
    signup_payload = {
        "username": "staker2",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Two",
        "staker_withdrawer_pubkey": "77777777777777777777777777777777",
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


def test_auth_me_without_token(client) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_login_inactive_user(client) -> None:
    signup_payload = {
        "username": "inactive_staker",
        "password": "secret123",
        "role": "staker",
        "alias": "Inactive Staker",
        "staker_withdrawer_pubkey": "88888888888888888888888888888888",
        "is_active": False,
    }
    client.post("/auth/signup", json=signup_payload)

    response = client.post(
        "/auth/login",
        data={"username": "inactive_staker", "password": "secret123"},
    )
    assert response.status_code == 403
