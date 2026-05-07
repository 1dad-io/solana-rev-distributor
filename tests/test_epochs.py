from tests.conftest import DEMO_EPOCH, DEMO_VOTE_ACCOUNT, write_demo_validator_rewards_file
from tests.pubkeys import make_staker_pubkey, make_validator_pubkey


def test_validator_can_import_epoch_context(client) -> None:
    validator_identity_pubkey = make_validator_pubkey(1)

    signup_payload = {
        "username": "test_validator_epoch_a",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Epoch A",
        "validator_identity_pubkey": validator_identity_pubkey,
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
    assert data["validator_identity_pubkey"] == validator_identity_pubkey
    assert data["cluster"] == "testnet"
    assert data["epoch"] == DEMO_EPOCH
    assert data["block_rewards_lamports"] == 1_000_000_000
    assert data["uptime_bps"] == 10000


def test_validator_can_get_epoch_context(client) -> None:
    validator_identity_pubkey = make_validator_pubkey(2)

    signup_payload = {
        "username": "test_validator_epoch_b",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Epoch B",
        "validator_identity_pubkey": validator_identity_pubkey,
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

    import_response = client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": DEMO_EPOCH,
            "block_rewards_lamports": 1_000_000_000,
            "uptime_bps": 10000,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert import_response.status_code == 201

    response = client.get(
        f"/validators/me/epochs/{DEMO_EPOCH}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["validator_identity_pubkey"] == validator_identity_pubkey
    assert data["cluster"] == "testnet"
    assert data["epoch"] == DEMO_EPOCH
    assert data["block_rewards_lamports"] == 1_000_000_000
    assert data["uptime_bps"] == 10000


def test_validator_cannot_get_missing_epoch_context(client) -> None:
    signup_payload = {
        "username": "test_validator_epoch_c",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Epoch C",
        "validator_identity_pubkey": make_validator_pubkey(3),
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
    assert response.json()["detail"] == "Epoch reward context not found"


def test_staker_cannot_import_epoch_context(client) -> None:
    signup_payload = {
        "username": "test_staker_epoch_forbidden_a",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Epoch Forbidden A",
        "staker_withdrawer_pubkey": make_staker_pubkey(4),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_staker_epoch_forbidden_a", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": DEMO_EPOCH,
            "block_rewards_lamports": 1_000_000_000,
            "uptime_bps": 10000,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_staker_cannot_get_validator_epoch_context(client) -> None:
    signup_payload = {
        "username": "test_staker_epoch_forbidden_b",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Epoch Forbidden B",
        "staker_withdrawer_pubkey": make_staker_pubkey(5),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_staker_epoch_forbidden_b", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        f"/validators/me/epochs/{DEMO_EPOCH}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_validator_import_epoch_context_requires_authentication(client) -> None:
    response = client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": DEMO_EPOCH,
            "block_rewards_lamports": 1_000_000_000,
            "uptime_bps": 10000,
        },
    )

    assert response.status_code == 401


def test_validator_get_epoch_context_requires_authentication(client) -> None:
    response = client.get(f"/validators/me/epochs/{DEMO_EPOCH}")
    assert response.status_code == 401
