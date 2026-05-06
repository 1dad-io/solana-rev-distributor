from tests.conftest import DEMO_VOTE_ACCOUNT


def test_validator_can_create_default_policy(client) -> None:
    signup_payload = {
        "username": "validator_policy_default",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy Default",
        "validator_identity_pubkey": "dddddddddddddddddddddddddddddddd",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_default", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 10000,
            "block_rewards_bps_back": 5000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["validator_identity_pubkey"] == "dddddddddddddddddddddddddddddddd"
    assert data["staker_withdrawer_pubkey"] is None
    assert data["is_default"] is True
    assert data["mev_bps_back"] == 10000
    assert data["block_rewards_bps_back"] == 5000
    assert data["valid_from_epoch"] is None
    assert data["valid_to_epoch"] is None
    assert data["is_active"] is True


def test_validator_can_create_individual_policy(client) -> None:
    signup_payload = {
        "username": "validator_policy_individual",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy Individual",
        "validator_identity_pubkey": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_individual", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "is_default": False,
            "mev_bps_back": 9000,
            "block_rewards_bps_back": 4000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["validator_identity_pubkey"] == "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    assert data["staker_withdrawer_pubkey"] == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    assert data["is_default"] is False
    assert data["mev_bps_back"] == 9000
    assert data["block_rewards_bps_back"] == 4000
    assert data["valid_from_epoch"] is None
    assert data["valid_to_epoch"] is None
    assert data["is_active"] is True


def test_validator_can_list_own_policies(client) -> None:
    signup_payload = {
        "username": "validator_policy_list",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy List",
        "validator_identity_pubkey": "1111aaaabbbbccccddddeeeeffff0000",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
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
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 10000,
            "block_rewards_bps_back": 5000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "is_default": False,
            "mev_bps_back": 8000,
            "block_rewards_bps_back": 3000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/validators/me/policies",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(
        policy["validator_identity_pubkey"] == "1111aaaabbbbccccddddeeeeffff0000"
        for policy in data
    )


def test_staker_cannot_create_policy(client) -> None:
    signup_payload = {
        "username": "staker_policy_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Policy Forbidden",
        "staker_withdrawer_pubkey": "cccccccccccccccccccccccccccccccc",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_policy_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 10000,
            "block_rewards_bps_back": 5000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_validator_cannot_create_duplicate_default_policy(client) -> None:
    signup_payload = {
        "username": "validator_policy_dup_default",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy Dup Default",
        "validator_identity_pubkey": "dupdefaultvalidator1111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_dup_default", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    first_response = client.post(
        "/validators/me/policies",
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
    assert first_response.status_code == 201

    second_response = client.post(
        "/validators/me/policies",
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
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "An identical reward policy already exists"


def test_validator_cannot_create_duplicate_individual_policy(client) -> None:
    signup_payload = {
        "username": "validator_policy_dup_individual",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy Dup Individual",
        "validator_identity_pubkey": "dupindividualvalidator11111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_dup_individual", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    first_response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": "abababababababababababababababab",
            "is_default": False,
            "mev_bps_back": 8000,
            "block_rewards_bps_back": 3500,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": "abababababababababababababababab",
            "is_default": False,
            "mev_bps_back": 8000,
            "block_rewards_bps_back": 3500,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "An identical reward policy already exists"


def test_validator_cannot_update_policy_into_duplicate(client) -> None:
    signup_payload = {
        "username": "validator_policy_dup_update",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy Dup Update",
        "validator_identity_pubkey": "dupupdatevalidator11111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_dup_update", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    first_response = client.post(
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
    assert first_response.status_code == 201
    first_policy_id = first_response.json()["id"]

    second_response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": "cdcdcdcdcdcdcdcdcdcdcdcdcdcdcdcd",
            "is_default": False,
            "mev_bps_back": 9000,
            "block_rewards_bps_back": 4000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second_response.status_code == 201
    second_policy_id = second_response.json()["id"]

    update_response = client.put(
        f"/validators/me/policies/{second_policy_id}",
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
    assert update_response.status_code == 409
    assert update_response.json()["detail"] == "An identical reward policy already exists"
    assert first_policy_id != second_policy_id


def test_validator_gets_404_when_updating_missing_policy(client) -> None:
    signup_payload = {
        "username": "validator_policy_missing_update",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy Missing Update",
        "validator_identity_pubkey": "missingupdatevalidator1111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_missing_update", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.put(
        "/validators/me/policies/999999",
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

    assert response.status_code == 404
    assert response.json()["detail"] == "Reward policy not found"


def test_validator_cannot_update_other_validators_policy(client) -> None:
    first_signup_payload = {
        "username": "validator_policy_owner_a",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy Owner A",
        "validator_identity_pubkey": "policyownera1111111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=first_signup_payload)

    second_signup_payload = {
        "username": "validator_policy_owner_b",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Policy Owner B",
        "validator_identity_pubkey": "policyownerb1111111111111111111111",
        "vote_account_pubkey": "VoteAccOwnerB111111111111111111111111111111111",
        "is_active": True,
    }
    client.post("/auth/signup", json=second_signup_payload)

    first_login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_owner_a", "password": "secret123"},
    )
    first_token = first_login_response.json()["access_token"]

    second_login_response = client.post(
        "/auth/login",
        data={"username": "validator_policy_owner_b", "password": "secret123"},
    )
    second_token = second_login_response.json()["access_token"]

    create_response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 6000,
            "block_rewards_bps_back": 3000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {first_token}"},
    )
    assert create_response.status_code == 201
    policy_id = create_response.json()["id"]

    update_response = client.put(
        f"/validators/me/policies/{policy_id}",
        json={
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 7000,
            "block_rewards_bps_back": 3500,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {second_token}"},
    )

    assert update_response.status_code == 404
    assert update_response.json()["detail"] == "Reward policy not found"


def test_staker_cannot_list_validator_policies(client) -> None:
    signup_payload = {
        "username": "staker_policy_list_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Policy List Forbidden",
        "staker_withdrawer_pubkey": "edededededededededededededededed",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_policy_list_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/validators/me/policies",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_staker_cannot_update_policy(client) -> None:
    signup_payload = {
        "username": "staker_policy_update_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Policy Update Forbidden",
        "staker_withdrawer_pubkey": "fefefefefefefefefefefefefefefefe",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_policy_update_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.put(
        "/validators/me/policies/1",
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
