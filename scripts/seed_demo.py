from pathlib import Path

from app.config import settings
from app.db import SessionLocal, engine, init_db
from app.models.reward_policy import RewardPolicy
from app.models.user import User
from app.models.validator import Validator
from app.security import hash_password
from app.services.epoch_import_service import import_epoch_reward_context
from app.services.reward_calculation_service import calculate_rewards_for_epoch
from app.services.stake_import_service import import_stake_snapshot
from tests.conftest import (
    DEMO_EPOCH,
    DEMO_STAKER_ALIAS,
    DEMO_STAKER_PASSWORD,
    DEMO_STAKER_USERNAME,
    DEMO_STAKER_WITHDRAWER,
    DEMO_VALIDATOR_ALIAS,
    DEMO_VALIDATOR_IDENTITY,
    DEMO_VALIDATOR_PASSWORD,
    DEMO_VALIDATOR_USERNAME,
    DEMO_VOTE_ACCOUNT,
    write_demo_stakes_file,
    write_demo_validator_rewards_file,
)


def runtime_db_path() -> Path:
    database_url = settings.database_url
    if not database_url.startswith("sqlite:///"):
        raise ValueError("This demo seed supports only sqlite:/// database URLs")
    return Path(database_url.removeprefix("sqlite:///"))


def main() -> None:
    engine.dispose()

    db_path = runtime_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    write_demo_stakes_file()
    write_demo_validator_rewards_file()

    init_db()

    db = SessionLocal()
    try:
        demo_validator_user = User(
            username=DEMO_VALIDATOR_USERNAME,
            password_hash=hash_password(DEMO_VALIDATOR_PASSWORD),
            role="validator",
            alias=DEMO_VALIDATOR_ALIAS,
            validator_identity_pubkey=DEMO_VALIDATOR_IDENTITY,
            is_active=True,
        )
        demo_staker_user = User(
            username=DEMO_STAKER_USERNAME,
            password_hash=hash_password(DEMO_STAKER_PASSWORD),
            role="staker",
            alias=DEMO_STAKER_ALIAS,
            staker_withdrawer_pubkey=DEMO_STAKER_WITHDRAWER,
            is_active=True,
        )

        demo_validator_record = Validator(
            identity_pubkey=DEMO_VALIDATOR_IDENTITY,
            vote_account_pubkey=DEMO_VOTE_ACCOUNT,
            alias=DEMO_VALIDATOR_ALIAS,
            cluster=settings.app_cluster,
            is_active=True,
        )

        db.add(demo_validator_user)
        db.add(demo_staker_user)
        db.add(demo_validator_record)
        db.commit()

        demo_policy = RewardPolicy(
            validator_identity_pubkey=DEMO_VALIDATOR_IDENTITY,
            cluster=settings.app_cluster,
            staker_withdrawer_pubkey=DEMO_STAKER_WITHDRAWER,
            is_default=False,
            mev_bps_back=10000,
            block_rewards_bps_back=5000,
            valid_from_epoch=None,
            valid_to_epoch=None,
            is_active=True,
        )
        db.add(demo_policy)
        db.commit()

        import_stake_snapshot(
            db=db,
            validator_identity_pubkey=DEMO_VALIDATOR_IDENTITY,
            vote_account_pubkey=DEMO_VOTE_ACCOUNT,
            epoch=DEMO_EPOCH,
        )

        import_epoch_reward_context(
            db=db,
            validator_identity_pubkey=DEMO_VALIDATOR_IDENTITY,
            vote_account_pubkey=DEMO_VOTE_ACCOUNT,
            epoch=DEMO_EPOCH,
            block_rewards_lamports=1_000_000_000,
            uptime_bps=10000,
        )

        rewards = calculate_rewards_for_epoch(
            db=db,
            validator_identity_pubkey=DEMO_VALIDATOR_IDENTITY,
            epoch=DEMO_EPOCH,
            force_recalculate=True,
        )

        print("Demo seed completed.")
        print(f"Runtime DB: {db_path}")
        print(f"Demo epoch: {DEMO_EPOCH}")
        print(f"Validator username: {DEMO_VALIDATOR_USERNAME}")
        print(f"Staker username: {DEMO_STAKER_USERNAME}")
        print(f"Rewards created: {len(rewards)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
