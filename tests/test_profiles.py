from tests.conftest import DEMO_EPOCH, DEMO_VOTE_ACCOUNT


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
    assert data["alias"] == "Staker Profile"
    assert data["staker_withdrawer_pubkey"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    assert data["is_active"] is True


def test_validator_can_get_own_profile(client) -> None:
    signup_payload = {
        "username": "validator_profile",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Profile",
        "validator_identity_pubkey": "99999999999999999999999999999999",
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
    assert data["validator_identity_pubkey"] == "99999999999999999999999999999999"
    assert data["vote_account_pubkey"] == DEMO_VOTE_ACCOUNT
    assert data["is_active"] is True


def test_staker_can_update_own_profile(client) -> None:
    signup_payload = {
        "username": "staker_update",
        "password": "secret123",
        "role": "staker",
        "alias": "Old Alias",
        "staker_withdrawer_pubkey": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
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
    assert data["username"] == "staker_update"
    assert data["alias"] == "New Alias"
    assert data["staker_withdrawer_pubkey"] == "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    assert data["is_active"] is False


def test_validator_can_update_own_profile(client) -> None:
    signup_payload = {
        "username": "validator_update",
        "password": "secret123",
        "role": "validator",
        "alias": "Old Validator Alias",
        "validator_identity_pubkey": "aaaaaaaa111111111111111111111111",
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
    assert data["username"] == "validator_update"
    assert data["alias"] == "New Validator Alias"
    assert data["validator_identity_pubkey"] == "aaaaaaaa111111111111111111111111"
    assert data["vote_account_pubkey"] == DEMO_VOTE_ACCOUNT
    assert data["is_active"] is False


def test_staker_cannot_access_validator_me(client) -> None:
    signup_payload = {
        "username": "staker_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Forbidden",
        "staker_withdrawer_pubkey": "dddddddddddddddddddddddddddddddd",
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


def test_inactive_validator_cannot_create_policy(client) -> None:
    signup_payload = {
        "username": "validator_inactive_policy",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Inactive Policy",
        "validator_identity_pubkey": "inactivepolicy11111111111111111111",
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
        "validator_identity_pubkey": "inactivepolicyupdate1111111111111",
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
        "validator_identity_pubkey": "inactivestakesimport111111111111",
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
        "validator_identity_pubkey": "inactiveepochimport1111111111111",
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
        "validator_identity_pubkey": "inactiverewardscalc1111111111111",
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
