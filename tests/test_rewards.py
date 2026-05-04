from tests.conftest import (
    DEMO_EPOCH,
    DEMO_STAKER_WITHDRAWER,
    DEMO_VOTE_ACCOUNT,
    write_demo_stakes_file,
    write_demo_validator_rewards_file,
)


def test_validator_can_calculate_rewards_and_staker_can_view_them(client) -> None:
    validator_signup = {
        "username": "test_validator_rewards_a",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Rewards A",
        "validator_identity_pubkey": "TestVa1idatorRewardsA11111111111111111111",
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

    create_validator_payload = {
        "identity_pubkey": "TestVa1idatorRewardsA11111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "alias": "Test Validator Rewards A",
        "cluster": "testnet",
        "is_active": True,
    }
    client.post("/validators", json=create_validator_payload)

    staker_signup = {
        "username": "test_staker_rewards_a",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Rewards A",
        "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
        "is_active": True,
    }
    client.post("/auth/signup", json=staker_signup)

    validator_login = client.post(
        "/auth/login",
        data={"username": "test_validator_rewards_a", "password": "secret123"},
    )
    validator_token = validator_login.json()["access_token"]

    staker_login = client.post(
        "/auth/login",
        data={"username": "test_staker_rewards_a", "password": "secret123"},
    )
    staker_token = staker_login.json()["access_token"]

    client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
            "is_default": False,
            "mev_bps_back": 10000,
            "block_rewards_bps_back": 5000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    write_demo_stakes_file()
    write_demo_validator_rewards_file()

    client.post(
        "/validators/me/stakes/import",
        json={"epoch": DEMO_EPOCH},
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": DEMO_EPOCH,
            "block_rewards_lamports": 1000000000,
            "uptime_bps": 10000,
        },
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    calc_response = client.post(
        "/validators/me/rewards/calculate",
        json={"epoch": DEMO_EPOCH, "force_recalculate": True},
        headers={"Authorization": f"Bearer {validator_token}"},
    )
    assert calc_response.status_code == 201

    calc_data = calc_response.json()
    assert len(calc_data) == 1
    assert calc_data[0]["status"] == "calculated"
    assert calc_data[0]["payable_reward_lamports"] > 0

    validator_rewards_response = client.get(
        "/validators/me/rewards",
        headers={"Authorization": f"Bearer {validator_token}"},
    )
    assert validator_rewards_response.status_code == 200
    assert len(validator_rewards_response.json()) == 1

    staker_rewards_response = client.get(
        "/stakers/me/rewards",
        headers={"Authorization": f"Bearer {staker_token}"},
    )
    assert staker_rewards_response.status_code == 200
    staker_rewards = staker_rewards_response.json()
    assert len(staker_rewards) == 1
    assert staker_rewards[0]["staker_withdrawer_pubkey"] == DEMO_STAKER_WITHDRAWER

    staker_stats_response = client.get(
        "/stakers/me/stats",
        headers={"Authorization": f"Bearer {staker_token}"},
    )
    assert staker_stats_response.status_code == 200
    stats = staker_stats_response.json()
    assert stats["rewards_count"] == 1
    assert stats["epochs_count"] == 1
    assert stats["stake_accounts_count"] == 1
    assert stats["payable_total_lamports"] > 0


def test_reward_without_policy_creates_error_status(client) -> None:
    validator_signup = {
        "username": "test_validator_rewards_b",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Rewards B",
        "validator_identity_pubkey": "TestVa1idatorRewardsB11111111111111111111",
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

    create_validator_payload = {
        "identity_pubkey": "TestVa1idatorRewardsB11111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "alias": "Test Validator Rewards B",
        "cluster": "testnet",
        "is_active": True,
    }
    client.post("/validators", json=create_validator_payload)

    staker_signup = {
        "username": "test_staker_rewards_b",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Rewards B",
        "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
        "is_active": True,
    }
    client.post("/auth/signup", json=staker_signup)

    validator_login = client.post(
        "/auth/login",
        data={"username": "test_validator_rewards_b", "password": "secret123"},
    )
    validator_token = validator_login.json()["access_token"]

    write_demo_stakes_file()
    write_demo_validator_rewards_file()

    client.post(
        "/validators/me/stakes/import",
        json={"epoch": DEMO_EPOCH},
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": DEMO_EPOCH,
            "block_rewards_lamports": 1000000000,
            "uptime_bps": 10000,
        },
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    calc_response = client.post(
        "/validators/me/rewards/calculate",
        json={"epoch": DEMO_EPOCH, "force_recalculate": True},
        headers={"Authorization": f"Bearer {validator_token}"},
    )
    assert calc_response.status_code == 201

    data = calc_response.json()
    assert len(data) == 1
    assert data[0]["status"] == "error_no_policy"
    assert data[0]["payable_reward_lamports"] == 0
