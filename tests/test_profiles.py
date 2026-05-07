from tests.conftest import DEMO_EPOCH, DEMO_VOTE_ACCOUNT
from tests.pubkeys import make_staker_pubkey, make_validator_pubkey


def test_staker_can_get_own_profile(client) -> None:
    staker_withdrawer_pubkey = make_staker_pubkey(1)

    signup_payload = {
        "username": "staker_profile",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Profile",
        "staker_withdrawer_pubkey": staker_withdrawer_pubkey,
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
    assert data["staker_withdrawer_pubkey"] == staker_withdrawer_pubkey
    assert data["is_active"] is True


def test_validator_can_get_own_profile(client) -> None:
    validator_identity_pubkey = make_validator_pubkey(2)

    signup_payload = {
        "username": "validator_profile",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Profile",
        "validator_identity_pubkey": validator_identity_pubkey,
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
    assert data["validator_identity_pubkey"] == validator_identity_pubkey
    assert data["is_active"] is True


def test_staker_can_update_own_profile(client) -> None:
    staker_withdrawer_pubkey = make_staker_pubkey(3)

    signup_payload = {
        "username": "staker_update",
        "password": "secret123",
        "role": "staker",
        "alias": "Old Alias",
        "staker_withdrawer_pubkey": staker_withdrawer_pubkey,
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
    assert data["staker_withdrawer_pubkey"] == staker_withdrawer_pubkey


def test_validator_can_update_own_profile(client) -> None:
    validator_identity_pubkey = make_validator_pubkey(4)

    signup_payload = {
        "username": "validator_update",
        "password": "secret123",
        "role": "validator",
        "alias": "Old Validator Alias",
        "validator_identity_pubkey": validator_identity_pubkey,
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
    assert data["is_active"] is False
    assert data["validator_identity_pubkey"] == validator_identity_pubkey


def test_staker_cannot_access_validator_me(client) -> None:
    signup_payload = {
        "username": "staker_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Forbidden",
        "staker_withdrawer_pubkey": make_staker_pubkey(5),
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
        "validator_identity_pubkey": make_validator_pubkey(6),
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


def test_staker_profile_requires_authentication(client) -> None:
    response = client.get("/stakers/me")
    assert response.status_code == 401


def test_validator_profile_requires_authentication(client) -> None:
    response = client.get("/validators/me")
    assert response.status_code == 401


def test_staker_update_requires_authentication(client) -> None:
    response = client.put(
        "/stakers/me",
        json={"alias": "No Auth", "is_active": True},
    )
    assert response.status_code == 401


def test_validator_update_requires_authentication(client) -> None:
    response = client.put(
        "/validators/me",
        json={"alias": "No Auth", "is_active": True},
    )
    assert response.status_code == 401


def test_staker_cannot_update_validator_profile(client) -> None:
    signup_payload = {
        "username": "staker_update_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Update Forbidden",
        "staker_withdrawer_pubkey": make_staker_pubkey(7),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_update_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.put(
        "/validators/me",
        json={"alias": "Should Not Work", "is_active": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_validator_cannot_update_staker_profile(client) -> None:
    signup_payload = {
        "username": "validator_update_forbidden",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Update Forbidden",
        "validator_identity_pubkey": make_validator_pubkey(8),
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_update_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.put(
        "/stakers/me",
        json={"alias": "Should Not Work", "is_active": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_inactive_staker_can_read_own_profile(client) -> None:
    signup_payload = {
        "username": "staker_inactive_read",
        "password": "secret123",
        "role": "staker",
        "alias": "Inactive Read Staker",
        "staker_withdrawer_pubkey": make_staker_pubkey(1),
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_inactive_read", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    deactivate_response = client.put(
        "/stakers/me",
        json={"alias": "Inactive Read Staker", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    response = client.get(
        "/stakers/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "staker_inactive_read"
    assert data["role"] == "staker"
    assert data["is_active"] is False


def test_inactive_validator_can_read_own_profile(client) -> None:
    signup_payload = {
        "username": "validator_inactive_read",
        "password": "secret123",
        "role": "validator",
        "alias": "Inactive Read Validator",
        "validator_identity_pubkey": make_validator_pubkey(2),
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_inactive_read", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    deactivate_response = client.put(
        "/validators/me",
        json={"alias": "Inactive Read Validator", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    response = client.get(
        "/validators/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "validator_inactive_read"
    assert data["role"] == "validator"
    assert data["is_active"] is False


def test_inactive_validator_cannot_create_policy(client) -> None:
    signup_payload = {
        "username": "validator_inactive_policy",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Inactive Policy",
        "validator_identity_pubkey": make_validator_pubkey(3),
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_inactive_policy", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    deactivate_response = client.put(
        "/validators/me",
        json={"alias": "Validator Inactive Policy", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 5000,
            "block_rewards_bps_back": 2500,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_inactive_validator_cannot_update_policy(client) -> None:
    signup_payload = {
        "username": "validator_inactive_policy_update",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Inactive Policy Update",
        "validator_identity_pubkey": make_validator_pubkey(4),
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_inactive_policy_update", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    create_policy_response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 5000,
            "block_rewards_bps_back": 2500,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_policy_response.status_code == 201
    policy_id = create_policy_response.json()["id"]

    deactivate_response = client.put(
        "/validators/me",
        json={"alias": "Validator Inactive Policy Update", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    response = client.put(
        f"/validators/me/policies/{policy_id}",
        json={
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 7000,
            "block_rewards_bps_back": 3000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_inactive_validator_cannot_import_stakes(client) -> None:
    signup_payload = {
        "username": "validator_inactive_stakes_import",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Inactive Stakes Import",
        "validator_identity_pubkey": make_validator_pubkey(5),
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_inactive_stakes_import", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    deactivate_response = client.put(
        "/validators/me",
        json={"alias": "Validator Inactive Stakes Import", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    response = client.post(
        "/validators/me/stakes/import",
        json={"epoch": DEMO_EPOCH},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_inactive_validator_cannot_import_epoch_context(client) -> None:
    signup_payload = {
        "username": "validator_inactive_epoch_import",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Inactive Epoch Import",
        "validator_identity_pubkey": make_validator_pubkey(6),
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_inactive_epoch_import", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    deactivate_response = client.put(
        "/validators/me",
        json={"alias": "Validator Inactive Epoch Import", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    response = client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": DEMO_EPOCH,
            "block_rewards_lamports": 1000000000,
            "uptime_bps": 10000,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_inactive_validator_cannot_calculate_rewards(client) -> None:
    signup_payload = {
        "username": "validator_inactive_rewards_calc",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Inactive Rewards Calc",
        "validator_identity_pubkey": make_validator_pubkey(7),
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_inactive_rewards_calc", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    deactivate_response = client.put(
        "/validators/me",
        json={"alias": "Validator Inactive Rewards Calc", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    response = client.post(
        "/validators/me/rewards/calculate",
        json={"epoch": DEMO_EPOCH, "force_recalculate": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
