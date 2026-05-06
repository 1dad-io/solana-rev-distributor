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
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

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
        f"/validators/me/rewards?epoch={DEMO_EPOCH}",
        headers={"Authorization": f"Bearer {validator_token}"},
    )
    assert validator_rewards_response.status_code == 200
    assert len(validator_rewards_response.json()) == 1

    staker_rewards_response = client.get(
        f"/stakers/me/rewards?epoch={DEMO_EPOCH}",
        headers={"Authorization": f"Bearer {staker_token}"},
    )
    assert staker_rewards_response.status_code == 200
    staker_rewards = staker_rewards_response.json()
    assert len(staker_rewards) == 1
    assert staker_rewards[0]["staker_withdrawer_pubkey"] == DEMO_STAKER_WITHDRAWER

    staker_stats_response = client.get(
        f"/stakers/me/stats?epoch={DEMO_EPOCH}",
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
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

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


def test_reward_uses_individual_policy_over_default_policy(client) -> None:
    validator_signup = {
        "username": "test_validator_rewards_priority_a",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Rewards Priority A",
        "validator_identity_pubkey": "PriorityValidatorA11111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

    staker_signup = {
        "username": "test_staker_rewards_priority_a",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Rewards Priority A",
        "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
        "is_active": True,
    }
    client.post("/auth/signup", json=staker_signup)

    validator_login = client.post(
        "/auth/login",
        data={"username": "test_validator_rewards_priority_a", "password": "secret123"},
    )
    validator_token = validator_login.json()["access_token"]

    client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 1000,
            "block_rewards_bps_back": 1000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {validator_token}"},
    )

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

    rewards = calc_response.json()
    assert len(rewards) == 1
    assert rewards[0]["status"] == "calculated"
    assert rewards[0]["mev_bps_back_used"] == 10000
    assert rewards[0]["block_rewards_bps_back_used"] == 5000


def test_reward_uses_default_policy_when_individual_policy_absent(client) -> None:
    validator_signup = {
        "username": "test_validator_rewards_priority_b",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Rewards Priority B",
        "validator_identity_pubkey": "PriorityValidatorB11111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

    staker_signup = {
        "username": "test_staker_rewards_priority_b",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Rewards Priority B",
        "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
        "is_active": True,
    }
    client.post("/auth/signup", json=staker_signup)

    validator_login = client.post(
        "/auth/login",
        data={"username": "test_validator_rewards_priority_b", "password": "secret123"},
    )
    validator_token = validator_login.json()["access_token"]

    client.post(
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

    rewards = calc_response.json()
    assert len(rewards) == 1
    assert rewards[0]["status"] == "calculated"
    assert rewards[0]["mev_bps_back_used"] == 7000
    assert rewards[0]["block_rewards_bps_back_used"] == 3000


def test_reward_ignores_inactive_individual_policy_and_uses_default_policy(client) -> None:
    validator_signup = {
        "username": "test_validator_rewards_priority_c",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Rewards Priority C",
        "validator_identity_pubkey": "PriorityValidatorC11111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

    staker_signup = {
        "username": "test_staker_rewards_priority_c",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Rewards Priority C",
        "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
        "is_active": True,
    }
    client.post("/auth/signup", json=staker_signup)

    validator_login = client.post(
        "/auth/login",
        data={"username": "test_validator_rewards_priority_c", "password": "secret123"},
    )
    validator_token = validator_login.json()["access_token"]

    default_policy_response = client.post(
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
        headers={"Authorization": f"Bearer {validator_token}"},
    )
    assert default_policy_response.status_code == 201

    inactive_individual_response = client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
            "is_default": False,
            "mev_bps_back": 10000,
            "block_rewards_bps_back": 5000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": False,
        },
        headers={"Authorization": f"Bearer {validator_token}"},
    )
    assert inactive_individual_response.status_code == 201

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

    rewards = calc_response.json()
    assert len(rewards) == 1
    assert rewards[0]["status"] == "calculated"
    assert rewards[0]["mev_bps_back_used"] == 7000
    assert rewards[0]["block_rewards_bps_back_used"] == 3000


def test_reward_uses_epoch_limited_individual_policy_for_matching_epoch(client) -> None:
    validator_signup = {
        "username": "test_validator_rewards_priority_d",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Rewards Priority D",
        "validator_identity_pubkey": "PriorityValidatorD11111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

    staker_signup = {
        "username": "test_staker_rewards_priority_d",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Rewards Priority D",
        "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
        "is_active": True,
    }
    client.post("/auth/signup", json=staker_signup)

    validator_login = client.post(
        "/auth/login",
        data={"username": "test_validator_rewards_priority_d", "password": "secret123"},
    )
    validator_token = validator_login.json()["access_token"]

    client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 1000,
            "block_rewards_bps_back": 1000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
            "is_default": False,
            "mev_bps_back": 9000,
            "block_rewards_bps_back": 4000,
            "valid_from_epoch": DEMO_EPOCH,
            "valid_to_epoch": DEMO_EPOCH,
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

    rewards = calc_response.json()
    assert len(rewards) == 1
    assert rewards[0]["status"] == "calculated"
    assert rewards[0]["mev_bps_back_used"] == 9000
    assert rewards[0]["block_rewards_bps_back_used"] == 4000


def test_reward_falls_back_to_default_policy_outside_individual_policy_epoch_range(client) -> None:
    validator_signup = {
        "username": "test_validator_rewards_priority_e",
        "password": "secret123",
        "role": "validator",
        "alias": "Test Validator Rewards Priority E",
        "validator_identity_pubkey": "PriorityValidatorE11111111111111111111",
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

    staker_signup = {
        "username": "test_staker_rewards_priority_e",
        "password": "secret123",
        "role": "staker",
        "alias": "Test Staker Rewards Priority E",
        "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
        "is_active": True,
    }
    client.post("/auth/signup", json=staker_signup)

    validator_login = client.post(
        "/auth/login",
        data={"username": "test_validator_rewards_priority_e", "password": "secret123"},
    )
    validator_token = validator_login.json()["access_token"]

    client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": 6000,
            "block_rewards_bps_back": 2000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
            "is_default": False,
            "mev_bps_back": 9500,
            "block_rewards_bps_back": 4500,
            "valid_from_epoch": DEMO_EPOCH + 1,
            "valid_to_epoch": DEMO_EPOCH + 1,
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

    rewards = calc_response.json()
    assert len(rewards) == 1
    assert rewards[0]["status"] == "calculated"
    assert rewards[0]["mev_bps_back_used"] == 6000
    assert rewards[0]["block_rewards_bps_back_used"] == 2000
