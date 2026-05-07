from tests.conftest import DEMO_EPOCH, DEMO_VOTE_ACCOUNT, write_demo_stakes_file
from tests.pubkeys import make_staker_pubkey, make_validator_pubkey


def test_validator_can_import_stakes(client) -> None:
    validator_identity_pubkey = make_validator_pubkey(1)

    signup_payload = {
        "username": "test_validator_stakes_a",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Stakes A",
        "validator_identity_pubkey": validator_identity_pubkey,
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
    assert data["validator_identity_pubkey"] == validator_identity_pubkey
    assert data["cluster"] == "testnet"
    assert data["epoch"] == DEMO_EPOCH


def test_validator_can_list_imported_stake_accounts(client) -> None:
    signup_payload = {
        "username": "test_validator_stakes_b",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Stakes B",
        "validator_identity_pubkey": make_validator_pubkey(2),
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
    assert len(data) >= 1
    assert all(item["snapshot_id"] is not None for item in data)
    assert all(item["stake_pubkey"] for item in data)


def test_validator_cannot_list_missing_stake_accounts(client) -> None:
    signup_payload = {
        "username": "test_validator_stakes_c",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Stakes C",
        "validator_identity_pubkey": make_validator_pubkey(3),
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
    assert response.json()["detail"] == "Stake snapshot not found"


def test_validator_can_list_imported_stake_snapshots(client) -> None:
    validator_identity_pubkey = make_validator_pubkey(4)

    signup_payload = {
        "username": "test_validator_stakes_d",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Stakes D",
        "validator_identity_pubkey": validator_identity_pubkey,
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_validator_stakes_d", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    write_demo_stakes_file()

    import_response = client.post(
        "/validators/me/stakes/import",
        json={"epoch": DEMO_EPOCH},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert import_response.status_code == 201

    response = client.get(
        "/validators/me/stakes",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["validator_identity_pubkey"] == validator_identity_pubkey
    assert data[0]["epoch"] == DEMO_EPOCH


def test_staker_cannot_import_stakes(client) -> None:
    signup_payload = {
        "username": "test_staker_stakes_forbidden_a",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Stakes Forbidden A",
        "staker_withdrawer_pubkey": make_staker_pubkey(5),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_staker_stakes_forbidden_a", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/validators/me/stakes/import",
        json={"epoch": DEMO_EPOCH},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_staker_cannot_list_validator_stake_snapshots(client) -> None:
    signup_payload = {
        "username": "test_staker_stakes_forbidden_b",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Stakes Forbidden B",
        "staker_withdrawer_pubkey": make_staker_pubkey(6),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_staker_stakes_forbidden_b", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/validators/me/stakes",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_staker_cannot_list_validator_stake_accounts(client) -> None:
    signup_payload = {
        "username": "test_staker_stakes_forbidden_c",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Stakes Forbidden C",
        "staker_withdrawer_pubkey": make_staker_pubkey(7),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "test_staker_stakes_forbidden_c", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        f"/validators/me/stakes/{DEMO_EPOCH}/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_validator_import_stakes_requires_authentication(client) -> None:
    response = client.post(
        "/validators/me/stakes/import",
        json={"epoch": DEMO_EPOCH},
    )

    assert response.status_code == 401


def test_validator_list_stake_snapshots_requires_authentication(client) -> None:
    response = client.get("/validators/me/stakes")
    assert response.status_code == 401


def test_validator_list_stake_accounts_requires_authentication(client) -> None:
    response = client.get(f"/validators/me/stakes/{DEMO_EPOCH}/accounts")
    assert response.status_code == 401
