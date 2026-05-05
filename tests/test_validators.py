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
    assert data["id"] == 1
    assert data["identity_pubkey"] == payload["identity_pubkey"]
    assert data["vote_account_pubkey"] == payload["vote_account_pubkey"]
    assert data["alias"] == payload["alias"]
    assert data["cluster"] == payload["cluster"]
    assert data["is_active"] is True
    assert "created_at" in data
    assert "updated_at" in data


def test_list_validators(client) -> None:
    create_payload = {
        "identity_pubkey": "11111111111111111111111111111111",
        "vote_account_pubkey": "22222222222222222222222222222222",
        "alias": "Test Validator",
        "cluster": "testnet",
        "is_active": True,
    }
    client.post("/validators", json=create_payload)

    response = client.get("/validators")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["identity_pubkey"] == create_payload["identity_pubkey"]
    assert data[0]["vote_account_pubkey"] == create_payload["vote_account_pubkey"]
    assert data[0]["alias"] == create_payload["alias"]
    assert data[0]["cluster"] == create_payload["cluster"]
    assert data[0]["is_active"] is True
    assert "id" in data[0]
    assert "created_at" in data[0]
    assert "updated_at" in data[0]
