from tests.conftest import DEMO_EPOCH, DEMO_VOTE_ACCOUNT, write_demo_validator_rewards_file


def test_validator_can_import_epoch_context(client) -> None:
    signup_payload = {
        "username": "test_validator_epoch_a",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Epoch A",
        "validator_identity_pubkey": "TestVa1idatorEpochA1111111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_validator_epoch_a", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    write_demo_validator_rewards_file()

    response = client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": DEMO_EPOCH,
            "block_rewards_lamports": 1_000_000_000,
            "uptime_bps": 10000,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["validator_identity_pubkey"] == signup_payload["validator_identity_pubkey"]
    assert data["epoch"] == DEMO_EPOCH
    assert data["block_rewards_lamports"] == 1_000_000_000
    assert data["uptime_bps"] == 10000
    assert data["mev_revenue_lamports"] >= 0
    assert data["mev_commission_bps"] >= 0


def test_validator_can_get_epoch_context(client) -> None:
    signup_payload = {
        "username": "test_validator_epoch_b",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Epoch B",
        "validator_identity_pubkey": "TestVa1idatorEpochB1111111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_validator_epoch_b", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    write_demo_validator_rewards_file()

    client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": DEMO_EPOCH,
            "block_rewards_lamports": 1_000_000_000,
            "uptime_bps": 10000,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/validators/me/epochs/{DEMO_EPOCH}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["validator_identity_pubkey"] == signup_payload["validator_identity_pubkey"]
    assert data["epoch"] == DEMO_EPOCH


def test_validator_cannot_get_missing_epoch_context(client) -> None:
    signup_payload = {
        "username": "test_validator_epoch_c",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Epoch C",
        "validator_identity_pubkey": "TestVa1idatorEpochC1111111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_validator_epoch_c", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        f"/validators/me/epochs/{DEMO_EPOCH}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
