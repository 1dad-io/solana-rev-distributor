import json
from pathlib import Path

from app.config import settings


def test_validator_can_calculate_rewards_and_staker_can_view_them(client) -> None:
    validator_signup = {
        "username": "validator_rewards_demo",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Rewards Demo",
        "validator_identity_pubkey": "rewardvalidator00000000000000000001",
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

    staker_signup = {
        "username": "staker_rewards_demo",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Rewards Demo",
        "staker_withdrawer_pubkey": "rewardwithdrawer000000000000000001",
        "is_active": True,
    }
    client.post("/auth/signup", json=staker_signup)

    validator_login = client.post(
        "/auth/login",
        data={"username": "validator_rewards_demo", "password": "secret123"},
    )
    validator_token = validator_login.json()["access_token"]

    staker_login = client.post(
        "/auth/login",
        data={"username": "staker_rewards_demo", "password": "secret123"},
    )
    staker_token = staker_login.json()["access_token"]

    client.post(
        "/validators/me/policies",
        json={
            "staker_withdrawer_pubkey": "rewardwithdrawer000000000000000001",
            "is_default": False,
            "mev_bps_back": 10000,
            "block_rewards_bps_back": 5000,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True
        },
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    stakes_dir = Path(settings.stakes_dir)
    stakes_dir.mkdir(parents=True, exist_ok=True)
    epoch = 951
    stakes_payload = [
        {
            "stakePubkey": "rewardstake1111111111111111111111111",
            "stakeType": "Stake",
            "accountBalance": 1000,
            "creditsObserved": 123,
            "delegatedStake": 1000,
            "activeStake": 1000,
            "delegatedVoteAccountAddress": "rewardvote1111111111111111111111111",
            "activationEpoch": 900,
            "deactivationEpoch": None,
            "staker": "rewardstaker111111111111111111111111",
            "withdrawer": "rewardwithdrawer000000000000000001",
            "rentExemptReserve": 100
        }
    ]
    (stakes_dir / f"{epoch}.json").write_text(json.dumps(stakes_payload), encoding="utf-8")

    client.post(
        "/validators/me/stakes/import",
        json={"epoch": epoch},
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    rewards_dir = Path(settings.validator_rewards_dir)
    rewards_dir.mkdir(parents=True, exist_ok=True)
    rewards_payload = {
        "mev_revenue_lamports": 500000000,
        "mev_commission_bps": 10000
    }
    (rewards_dir / f"{epoch}.json").write_text(json.dumps(rewards_payload), encoding="utf-8")

    client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": epoch,
            "block_rewards_lamports": 1000000000,
            "uptime_bps": 10000
        },
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    calc_response = client.post(
        "/validators/me/rewards/calculate",
        json={"epoch": epoch, "force_recalculate": True},
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
    assert staker_rewards[0]["staker_withdrawer_pubkey"] == "rewardwithdrawer000000000000000001"

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
        "username": "validator_no_policy",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator No Policy",
        "validator_identity_pubkey": "rewardvalidator00000000000000000002",
        "is_active": True,
    }
    client.post("/auth/signup", json=validator_signup)

    staker_signup = {
        "username": "staker_no_policy",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker No Policy",
        "staker_withdrawer_pubkey": "rewardwithdrawer000000000000000002",
        "is_active": True,
    }
    client.post("/auth/signup", json=staker_signup)

    validator_login = client.post(
        "/auth/login",
        data={"username": "validator_no_policy", "password": "secret123"},
    )
    validator_token = validator_login.json()["access_token"]

    epoch = 952

    stakes_dir = Path(settings.stakes_dir)
    stakes_dir.mkdir(parents=True, exist_ok=True)
    (stakes_dir / f"{epoch}.json").write_text(
        json.dumps(
            [
                {
                    "stakePubkey": "rewardstake2222222222222222222222222",
                    "stakeType": "Stake",
                    "accountBalance": 1000,
                    "creditsObserved": 123,
                    "delegatedStake": 1000,
                    "activeStake": 1000,
                    "delegatedVoteAccountAddress": "rewardvote2222222222222222222222222",
                    "activationEpoch": 900,
                    "deactivationEpoch": None,
                    "staker": "rewardstaker222222222222222222222222",
                    "withdrawer": "rewardwithdrawer000000000000000002",
                    "rentExemptReserve": 100
                }
            ]
        ),
        encoding="utf-8",
    )

    client.post(
        "/validators/me/stakes/import",
        json={"epoch": epoch},
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    rewards_dir = Path(settings.validator_rewards_dir)
    rewards_dir.mkdir(parents=True, exist_ok=True)
    (rewards_dir / f"{epoch}.json").write_text(
        json.dumps(
            {
                "mev_revenue_lamports": 500000000,
                "mev_commission_bps": 10000
            }
        ),
        encoding="utf-8",
    )

    client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": epoch,
            "block_rewards_lamports": 1000000000,
            "uptime_bps": 10000
        },
        headers={"Authorization": f"Bearer {validator_token}"},
    )

    calc_response = client.post(
        "/validators/me/rewards/calculate",
        json={"epoch": epoch, "force_recalculate": True},
        headers={"Authorization": f"Bearer {validator_token}"},
    )
    assert calc_response.status_code == 201

    data = calc_response.json()
    assert len(data) == 1
    assert data[0]["status"] == "error_no_policy"
    assert data[0]["payable_reward_lamports"] == 0
