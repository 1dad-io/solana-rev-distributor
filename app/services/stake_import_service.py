import hashlib
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.stake_account import StakeAccount
from app.models.stake_snapshot import StakeSnapshot


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def import_stake_snapshot(
    db: Session,
    validator_identity_pubkey: str,
    epoch: int,
) -> StakeSnapshot:
    source_path = Path(settings.stakes_dir) / f"{epoch}.json"
    if not source_path.exists():
        raise FileNotFoundError(str(source_path))

    raw_text = source_path.read_text(encoding="utf-8")
    payload = json.loads(raw_text)

    if not isinstance(payload, list):
        raise ValueError("Stake snapshot file must contain a JSON array")

    existing_snapshot = (
        db.query(StakeSnapshot)
        .filter(StakeSnapshot.validator_identity_pubkey == validator_identity_pubkey)
        .filter(StakeSnapshot.cluster == settings.app_cluster)
        .filter(StakeSnapshot.epoch == epoch)
        .first()
    )

    if existing_snapshot:
        db.query(StakeAccount).filter(StakeAccount.snapshot_id == existing_snapshot.id).delete()
        db.delete(existing_snapshot)
        db.commit()

    snapshot = StakeSnapshot(
        validator_identity_pubkey=validator_identity_pubkey,
        cluster=settings.app_cluster,
        epoch=epoch,
        source_path=str(source_path),
        source_hash=_sha256_text(raw_text),
        records_count=len(payload),
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    for item in payload:
        account = StakeAccount(
            snapshot_id=snapshot.id,
            stake_pubkey=item.get("stakePubkey"),
            stake_type=item.get("stakeType"),
            account_balance_lamports=item.get("accountBalance"),
            credits_observed=item.get("creditsObserved"),
            delegated_stake_lamports=item.get("delegatedStake"),
            active_stake_lamports=item.get("activeStake"),
            delegated_vote_account_pubkey=item.get("delegatedVoteAccountAddress"),
            activation_epoch=item.get("activationEpoch"),
            deactivation_epoch=item.get("deactivationEpoch"),
            staker_authority=item.get("staker"),
            withdrawer_authority=item.get("withdrawer"),
            rent_exempt_reserve_lamports=item.get("rentExemptReserve"),
        )
        db.add(account)

    db.commit()
    return snapshot
