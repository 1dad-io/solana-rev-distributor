import json
from pathlib import Path

from app.config import settings


def test_validator_can_import_epoch_context(client) -> None:
    signup_payload = {
        "username": "validator_epoch_import",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Epoch Import",
        "validator_identity_pubkey": "ababaaaabbbbccccddddeeeeffff1111",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_epoch_import", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    rewards_dir = Path(settings.validator_rewards_dir)
    rewards_dir.mkdir(parents=True, exist_ok=True)
    epoch = 951

    payload = {
        "mev_revenue_lamports": 500000000,
        "mev_commission_bps": 10000
    }
    (rewards_dir / f"{epoch}.json").write_text(json.dumps(payload), encoding="utf-8")

    response = client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": epoch,
            "block_rewards_lamports": 1000000000,
            "uptime_bps": 10000
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["epoch"] == epoch
    assert data["mev_revenue_lamports"] == 500000000
    assert data["mev_commission_bps"] == 10000
    assert data["block_rewards_lamports"] == 1000000000


def test_validator_can_get_epoch_context(client) -> None:
    signup_payload = {
        "username": "validator_epoch_get",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Epoch Get",
        "validator_identity_pubkey": "cdcdaaaabbbbccccddddeeeeffff2222",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_epoch_get", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    rewards_dir = Path(settings.validator_rewards_dir)
    rewards_dir.mkdir(parents=True, exist_ok=True)
    epoch = 952

    payload = {
        "mev_revenue_lamports": 700000000,
        "mev_commission_bps": 8000
    }
    (rewards_dir / f"{epoch}.json").write_text(json.dumps(payload), encoding="utf-8")

    client.post(
        "/validators/me/epochs/import",
        json={
            "epoch": epoch,
            "block_rewards_lamports": 1500000000,
            "uptime_bps": 9500
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        f"/validators/me/epochs/{epoch}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["epoch"] == epoch
    assert data["mev_revenue_lamports"] == 700000000
    assert data["block_rewards_lamports"] == 1500000000
    assert data["uptime_bps"] == 9500


def test_staker_cannot_access_validator_epochs(client) -> None:
    signup_payload = {
        "username": "staker_epoch_forbidden",
        "password": "secret123",
        "role": "staker",
        "alias": "Staker Epoch Forbidden",
        "staker_withdrawer_pubkey": "efefaaaabbbbccccddddeeeeffff3333",
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "staker_epoch_forbidden", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/validators/me/epochs/951",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
