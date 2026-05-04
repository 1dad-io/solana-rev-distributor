import json
from pathlib import Path

from app.config import settings


def test_validator_can_import_stakes(client) -> None:
    signup_payload = {
        "username": "validator_stakes_import",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Stakes Import",
        "validator_identity_pubkey": "1212aaaabbbbccccddddeeeeffff1111",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_stakes_import", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    stakes_dir = Path(settings.stakes_dir)
    stakes_dir.mkdir(parents=True, exist_ok=True)
    epoch = 951

    payload = [
        {
            "stakePubkey": "stake111111111111111111111111111111",
            "stakeType": "Stake",
            "accountBalance": 1000,
            "creditsObserved": 123,
            "delegatedStake": 900,
            "activeStake": 900,
            "delegatedVoteAccountAddress": "vote1111111111111111111111111111111",
            "activationEpoch": 900,
            "deactivationEpoch": None,
            "staker": "staker111111111111111111111111111111",
            "withdrawer": "withdrawer1111111111111111111111111111",
            "rentExemptReserve": 100
        }
    ]
    (stakes_dir / f"{epoch}.json").write_text(json.dumps(payload), encoding="utf-8")

    response = client.post(
        "/validators/me/stakes/import",
        json={"epoch": epoch},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["epoch"] == epoch
    assert data["records_count"] == 1


def test_validator_can_list_imported_stake_accounts(client) -> None:
    signup_payload = {
        "username": "validator_stakes_list",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Stakes List",
        "validator_identity_pubkey": "3434aaaabbbbccccddddeeeeffff2222",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_stakes_list", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    stakes_dir = Path(settings.stakes_dir)
    stakes_dir.mkdir(parents=True, exist_ok=True)
    epoch = 952

    payload = [
        {
            "stakePubkey": "stake222222222222222222222222222222",
            "stakeType": "Stake",
            "accountBalance": 2000,
            "creditsObserved": 456,
            "delegatedStake": 1800,
            "activeStake": 1800,
            "delegatedVoteAccountAddress": "vote2222222222222222222222222222222",
            "activationEpoch": 901,
            "deactivationEpoch": None,
            "staker": "staker222222222222222222222222222222",
            "withdrawer": "withdrawer2222222222222222222222222222",
            "rentExemptReserve": 200
        }
    ]
    (stakes_dir / f"{epoch}.json").write_text(json.dumps(payload), encoding="utf-8")

    client.post(
        "/validators/me/stakes/import",
        json={"epoch": epoch},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/validators/me/stakes/{epoch}/accounts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["stake_pubkey"] == "stake222222222222222222222222222222"


def test_staker_cannot_import_stakes(client) -> None:
    signup_payload = {
        "username": "staker_stakes_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Stakes Forbidden",
        "staker_withdrawer_pubkey": "5656aaaabbbbccccddddeeeeffff3333",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_stakes_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/validators/me/stakes/import",
        json={"epoch": 951},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
