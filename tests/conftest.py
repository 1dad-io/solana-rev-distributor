from pathlib import Path
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import get_db
from app.main import app
from app.models import Base

DEMO_EPOCH = 0

DEMO_VALIDATOR_USERNAME = "demo_validator"
DEMO_VALIDATOR_PASSWORD = "secret123"
DEMO_VALIDATOR_ALIAS = "Demo Validator"
DEMO_VALIDATOR_IDENTITY = "Va1idator11111111111111111111111111111111111"
DEMO_VOTE_ACCOUNT = "VoteAcc111111111111111111111111111111111111"

DEMO_STAKER_USERNAME = "demo_staker"
DEMO_STAKER_PASSWORD = "secret123"
DEMO_STAKER_ALIAS = "Demo Staker"
DEMO_STAKER_WITHDRAWER = "Staker1111111111111111111111111111111111111"

DEMO_STAKE_PUBKEY = "StakeAcc11111111111111111111111111111111111"


def write_demo_stakes_file() -> Path:
    stakes_dir = Path(settings.stakes_dir)
    stakes_dir.mkdir(parents=True, exist_ok=True)

    payload = [
        {
            "stakePubkey": DEMO_STAKE_PUBKEY,
            "stakeType": "Stake",
            "accountBalance": 14889939721,
            "creditsObserved": 718890781,
            "delegatedStake": 14887656841,
            "activeStake": 14887656841,
            "delegatedVoteAccountAddress": DEMO_VOTE_ACCOUNT,
            "activationEpoch": 686,
            "deactivationEpoch": None,
            "staker": DEMO_STAKER_WITHDRAWER,
            "withdrawer": DEMO_STAKER_WITHDRAWER,
            "rentExemptReserve": 2282880,
        }
    ]

    output = stakes_dir / f"{DEMO_EPOCH}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def write_demo_validator_rewards_file() -> Path:
    rewards_dir = Path(settings.validator_rewards_dir)
    rewards_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "mev_revenue_lamports": 500000000,
        "mev_commission_bps": 10000,
    }

    output = rewards_dir / f"{DEMO_EPOCH}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


@pytest.fixture
def client(tmp_path: Path):
    test_db_path = tmp_path / "test_app.db"
    test_database_url = f"sqlite:///{test_db_path}"

    engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
    )

    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        class_=Session,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
