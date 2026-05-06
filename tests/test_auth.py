def test_signup_validator(client) -> None:
    payload = {
        "username": "validator1",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator User",
        "validator_identity_pubkey": "33333333333333333333333333333333",
        "vote_account_pubkey": "VoteAcc111111111111111111111111111111111111",
        "is_active": True,
    }

    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "validator1"
    assert data["role"] == "validator"
    assert data["alias"] == "Validator User"
    assert data["validator_identity_pubkey"] == "33333333333333333333333333333333"
    assert data["staker_withdrawer_pubkey"] is None
    assert data["is_active"] is True


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
    assert data["username"] == "staker1"
    assert data["role"] == "staker"
    assert data["alias"] == "Staker User"
    assert data["validator_identity_pubkey"] is None
    assert data["staker_withdrawer_pubkey"] == "44444444444444444444444444444444"
    assert data["is_active"] is True


def test_signup_duplicate_username_fails(client) -> None:
    payload = {
        "username": "duplicate_user",
        "password": "secret123",
        "role": "staker",
        "alias": "First User",
        "staker_withdrawer_pubkey": "66666666666666666666666666666666",
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
            "validator_identity_pubkey": "77777777777777777777777777777777",
            "vote_account_pubkey": "VoteAcc222222222222222222222222222222222222",
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
        "validator_identity_pubkey": "55555555555555555555555555555555",
        "vote_account_pubkey": "VoteAcc333333333333333333333333333333333333",
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
        "validator_identity_pubkey": "88888888888888888888888888888888",
        "vote_account_pubkey": "VoteAcc444444444444444444444444444444444444",
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
    assert data["alias"] == "Staker Two"
    assert data["validator_identity_pubkey"] is None
    assert data["staker_withdrawer_pubkey"] == "77777777777777777777777777777777"
    assert data["is_active"] is True


def test_auth_me_without_token_fails(client) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_inactive_staker_cannot_login(client) -> None:
    signup_payload = {
        "username": "staker_inactive_login",
        "password": "secret123",
        "role": "staker",
        "alias": "Inactive Staker",
        "staker_withdrawer_pubkey": "12121212121212121212121212121212",
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


def test_inactive_validator_cannot_login(client) -> None:
    signup_payload = {
        "username": "validator_inactive_login",
        "password": "secret123",
        "role": "validator",
        "alias": "Inactive Validator",
        "validator_identity_pubkey": "13131313131313131313131313131313",
        "vote_account_pubkey": "VoteAcc555555555555555555555555555555555555",
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
