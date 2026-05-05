from tests.conftest import DEMO_EPOCH, DEMO_VOTE_ACCOUNT, write_demo_stakes_file


def test_validator_can_import_stakes(client) -> None:
    signup_payload = {
        "username": "test_validator_stakes_a",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Stakes A",
        "validator_identity_pubkey": "TestVa1idatorStakesA111111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_validator_stakes_a", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    write_demo_stakes_file()

    response = client.post(
        "/validators/me/stakes/import",
        json={"epoch": DEMO_EPOCH},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["validator_identity_pubkey"] == signup_payload["validator_identity_pubkey"]
    assert data["epoch"] == DEMO_EPOCH
    assert data["records_count"] == 1


def test_validator_can_list_imported_stake_accounts(client) -> None:
    signup_payload = {
        "username": "test_validator_stakes_b",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Stakes B",
        "validator_identity_pubkey": "TestVa1idatorStakesB111111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_validator_stakes_b", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    write_demo_stakes_file()

    client.post(
        "/validators/me/stakes/import",
        json={"epoch": DEMO_EPOCH},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/validators/me/stakes/{DEMO_EPOCH}/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert "stake_pubkey" in data[0]
    assert data[0]["delegated_vote_account_pubkey"] == DEMO_VOTE_ACCOUNT


def test_validator_cannot_list_missing_stake_accounts(client) -> None:
    signup_payload = {
        "username": "test_validator_stakes_c",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Stakes C",
        "validator_identity_pubkey": "TestVa1idatorStakesC111111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_validator_stakes_c", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        f"/validators/me/stakes/{DEMO_EPOCH}/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
