from tests.conftest import DEMO_VOTE_ACCOUNT
from tests.pubkeys import make_validator_pubkey, make_vote_account_pubkey


def test_can_create_validator(client) -> None:
    validator_identity_pubkey = make_validator_pubkey(1)

    signup_payload = {
        "username": "validator_directory_a",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Directory A",
        "validator_identity_pubkey": validator_identity_pubkey,
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    response = client.get("/validators")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(
        item["identity_pubkey"] == validator_identity_pubkey
        for item in data
    )


def test_can_list_validators(client) -> None:
    first_validator_identity_pubkey = make_validator_pubkey(2)
    second_validator_identity_pubkey = make_validator_pubkey(3)

    first_signup_payload = {
        "username": "validator_directory_b1",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Directory B1",
        "validator_identity_pubkey": first_validator_identity_pubkey,
        "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
        "is_active": True,
    }
    client.post("/auth/signup", json=first_signup_payload)

    second_signup_payload = {
        "username": "validator_directory_b2",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Directory B2",
        "validator_identity_pubkey": second_validator_identity_pubkey,
        "vote_account_pubkey": make_vote_account_pubkey(4),
        "is_active": True,
    }
    client.post("/auth/signup", json=second_signup_payload)

    response = client.get("/validators")

    assert response.status_code == 200
    data = response.json()
    identities = [item["identity_pubkey"] for item in data]
    assert first_validator_identity_pubkey in identities
    assert second_validator_identity_pubkey in identities


def test_validator_directory_returns_expected_shape(client) -> None:
    validator_identity_pubkey = make_validator_pubkey(5)
    vote_account_pubkey = make_vote_account_pubkey(6)

    signup_payload = {
        "username": "validator_directory_c",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Directory C",
        "validator_identity_pubkey": validator_identity_pubkey,
        "vote_account_pubkey": vote_account_pubkey,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    response = client.get("/validators")

    assert response.status_code == 200
    data = response.json()
    matching = [
        item
        for item in data
        if item["identity_pubkey"] == validator_identity_pubkey
    ]
    assert len(matching) == 1

    validator = matching[0]
    assert validator["alias"] == "Validator Directory C"
    assert validator["cluster"] == "testnet"
    assert validator["is_active"] is True
    assert validator["vote_account_pubkey"] == vote_account_pubkey


def test_inactive_validator_remains_visible_in_directory(client) -> None:
    validator_identity_pubkey = make_validator_pubkey(7)
    vote_account_pubkey = make_vote_account_pubkey(8)

    signup_payload = {
        "username": "validator_directory_d",
        "password": "secret123",
        "role": "validator",
        "alias": "Validator Directory D",
        "validator_identity_pubkey": validator_identity_pubkey,
        "vote_account_pubkey": vote_account_pubkey,
        "is_active": True,
    }
    client.post("/auth/signup", json=signup_payload)

    login_response = client.post(
        "/auth/login",
        data={"username": "validator_directory_d", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    deactivate_response = client.put(
        "/validators/me",
        json={"alias": "Validator Directory D", "is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["is_active"] is False

    response = client.get("/validators")
    assert response.status_code == 200

    data = response.json()
    matching = [
        item
        for item in data
        if item["identity_pubkey"] == validator_identity_pubkey
    ]
    assert len(matching) == 1
    assert matching[0]["alias"] == "Validator Directory D"
    assert matching[0]["cluster"] == "testnet"
    assert matching[0]["vote_account_pubkey"] == vote_account_pubkey


def test_validators_directory_does_not_require_authentication(client) -> None:
    response = client.get("/validators")
    assert response.status_code == 200
