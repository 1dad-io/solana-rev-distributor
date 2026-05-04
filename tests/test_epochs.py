from tests.conftest import (
    DEMO_EPOCH,
    DEMO_VOTE_ACCOUNT,
    write_demo_validator_rewards_file,
)


def test_validator_can_import_epoch_context(client) -> None:
    signup_payload = {
        "username": "test_validator_epoch_a",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Epoch A",
        "validator_identity_pubkey": "TestVa1idatorEpochA1111111111111111111111",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    create_validator_payload = {
        "identity_pubkey": "TestVa1idatorEpochA1111111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "alias": "Test Validator Epoch A",
        "cluster": "testnet",
        "is_active": True,
    }
    client.post("/validators", json=create_validator_payload)

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
            "block_rewards_lamports": 1000000000,
            "uptime_bps": 10000,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["epoch"] == DEMO_EPOCH
    assert data["mev_revenue_lamports"] == 500000000
    assert data["mev_commission_bps"] == 10000
    assert data["block_rewards_lamports"] == 1000000000


def test_validator_can_get_epoch_context(client) -> None:
    signup_payload = {
        "username": "test_validator_epoch_b",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Epoch B",
        "validator_identity_pubkey": "TestVa1idatorEpochB1111111111111111111111",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    create_validator_payload = {
        "identity_pubkey": "TestVa1idatorEpochB1111111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "alias": "Test Validator Epoch B",
        "cluster": "testnet",
        "is_active": True,
    }
    client.post("/validators", json=create_validator_payload)

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
            "block_rewards_lamports": 1500000000,
            "uptime_bps": 9500,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/validators/me/epochs/{DEMO_EPOCH}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["epoch"] == DEMO_EPOCH
    assert data["mev_revenue_lamports"] == 500000000
    assert data["block_rewards_lamports"] == 1500000000
    assert data["uptime_bps"] == 9500


def test_staker_cannot_access_validator_epochs(client) -> None:
    signup_payload = {
        "username": "test_staker_epoch_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Epoch Forbidden",
        "staker_withdrawer_pubkey": "TestStakerEpochA1111111111111111111111111",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_staker_epoch_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        f"/validators/me/epochs/{DEMO_EPOCH}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
