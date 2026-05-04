def test_create_validator(client) -> None:
    payload = {
        "identity_pubkey": "11111111111111111111111111111111",
        "vote_account_pubkey": "22222222222222222222222222222222",
        "alias": "Test Validator",
        "cluster": "testnet",
        "is_active": True,
    }

    response = client.post("/validators", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["identity_pubkey"] == payload["identity_pubkey"]
    assert data["vote_account_pubkey"] == payload["vote_account_pubkey"]
    assert data["alias"] == payload["alias"]
    assert data["cluster"] == payload["cluster"]
    assert "id" not in data


def test_list_validators(client) -> None:
    response = client.get("/validators")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
