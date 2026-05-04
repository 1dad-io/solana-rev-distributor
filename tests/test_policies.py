def test_validator_can_create_default_policy(client) -> None:
    signup_payload = {
        "username": "validator_policy_default",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy Default",
        "validator_identity_pubkey": "dddddddddddddddddddddddddddddddd",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_default", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    payload = {
        "is_default": True,
        "mev_bps_back": 10000,
        "block_rewards_bps_back": 5000,
        "valid_from_epoch": None,
        "valid_to_epoch": None,
        "is_active": True
    }

    response = client.post(
        "/validators/me/policies",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["validator_identity_pubkey"] == "dddddddddddddddddddddddddddddddd"
    assert data["is_default"] is True
    assert data["mev_bps_back"] == 10000
    assert data["block_rewards_bps_back"] == 5000


def test_validator_can_create_individual_policy(client) -> None:
    signup_payload = {
        "username": "validator_policy_individual",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy Individual",
        "validator_identity_pubkey": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_individual", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    payload = {
        "staker_withdrawer_pubkey": "ffffffffffffffffffffffffffffffff",
        "is_default": False,
        "mev_bps_back": 10000,
        "block_rewards_bps_back": 2500,
        "valid_from_epoch": 900,
        "valid_to_epoch": 950,
        "is_active": True
    }

    response = client.post(
        "/validators/me/policies",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["staker_withdrawer_pubkey"] == "ffffffffffffffffffffffffffffffff"
    assert data["is_default"] is False
    assert data["valid_from_epoch"] == 900
    assert data["valid_to_epoch"] == 950


def test_validator_can_list_own_policies(client) -> None:
    signup_payload = {
        "username": "validator_policy_list",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy List",
        "validator_identity_pubkey": "1111aaaabbbbccccddddeeeeffff0000",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_list", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    client.post(
        "/validators/me/policies",
        json={
            "is_default": True,
            "mev_bps_back": 10000,
            "block_rewards_bps_back": 5000,
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/validators/me/policies",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_staker_cannot_access_validator_policies(client) -> None:
    signup_payload = {
        "username": "staker_policy_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Policy Forbidden",
        "staker_withdrawer_pubkey": "12121212121212121212121212121212",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_policy_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/validators/me/policies",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
