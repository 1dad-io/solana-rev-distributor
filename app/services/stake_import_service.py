import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.stake_account import StakeAccount
from app.models.stake_snapshot import StakeSnapshot


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _fetch_stakes_with_solana_cli(source_path: Path, vote_account_pubkey: str) -> None:
    solana_cli = shutil.which("solana")
    if solana_cli is None:
        raise FileNotFoundError(
            "Stake snapshot file not found and Solana CLI is not installed. "
            "Provide the JSON file manually or install Solana CLI."
        )

    source_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        solana_cli,
        "-u",
        settings.rpc_url,
        "stakes",
        vote_account_pubkey,
        "--output",
        "json",
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        timeout=settings.http_timeout_seconds,
    )

    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        raise ValueError(
            f"Failed to fetch stakes via Solana CLI: {stderr or stdout or 'unknown error'}"
        )

    source_path.write_text(result.stdout, encoding="utf-8")


def import_stake_snapshot(
    db: Session,
    validator_identity_pubkey: str,
    vote_account_pubkey: str,
    epoch: int,
) -> StakeSnapshot:
    source_path = Path(settings.stakes_dir) / f"{epoch}.json"

    if not source_path.exists():
        _fetch_stakes_with_solana_cli(
            source_path=source_path,
            vote_account_pubkey=vote_account_pubkey,
        )

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
