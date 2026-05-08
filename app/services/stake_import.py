import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.stake_account import StakeAccount
from app.models.stake_snapshot import StakeSnapshot


@dataclass(frozen=True)
class StakeSnapshotValues:
    validator_identity_pubkey: str
    epoch: int
    source_path: Path
    raw_text: str
    records_count: int


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_stakes_source_path(epoch: int) -> Path:
    return Path(settings.stakes_dir) / f"{epoch}.json"


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


def _ensure_stakes_source_file(source_path: Path, vote_account_pubkey: str) -> None:
    if source_path.exists():
        return

    _fetch_stakes_with_solana_cli(
        source_path=source_path,
        vote_account_pubkey=vote_account_pubkey,
    )


def _load_stakes_payload(source_path: Path) -> tuple[list[dict], str]:
    raw_text = source_path.read_text(encoding="utf-8")
    payload = json.loads(raw_text)

    if not isinstance(payload, list):
        raise ValueError("Stake snapshot file must contain a JSON array")

    normalized_payload: list[dict] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("Stake snapshot file must contain only JSON objects")
        normalized_payload.append(item)

    return normalized_payload, raw_text


def _get_existing_snapshot(
    db: Session,
    *,
    validator_identity_pubkey: str,
    epoch: int,
) -> StakeSnapshot | None:
    return (
        db.query(StakeSnapshot)
        .filter(StakeSnapshot.validator_identity_pubkey == validator_identity_pubkey)
        .filter(StakeSnapshot.cluster == settings.app_cluster)
        .filter(StakeSnapshot.epoch == epoch)
        .first()
    )


def _delete_existing_snapshot(
    db: Session,
    *,
    snapshot_id: int,
) -> None:
    db.query(StakeAccount).filter(StakeAccount.snapshot_id == snapshot_id).delete()
    db.query(StakeSnapshot).filter(StakeSnapshot.id == snapshot_id).delete()
    db.commit()


def _create_snapshot(
    db: Session,
    *,
    values: StakeSnapshotValues,
) -> StakeSnapshot:
    snapshot = StakeSnapshot(
        validator_identity_pubkey=values.validator_identity_pubkey,
        cluster=settings.app_cluster,
        epoch=values.epoch,
        source_path=str(values.source_path),
        source_hash=_sha256_text(values.raw_text),
        records_count=values.records_count,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot


def _build_stake_account(snapshot_id: int, item: dict) -> StakeAccount:
    return StakeAccount(
        snapshot_id=snapshot_id,
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


def _create_stake_accounts(
    db: Session,
    *,
    snapshot_id: int,
    payload: list[dict],
) -> None:
    for item in payload:
        db.add(_build_stake_account(snapshot_id, item))
    db.commit()


# pylint: disable=too-many-arguments
def import_stake_snapshot(
    db: Session,
    validator_identity_pubkey: str,
    vote_account_pubkey: str,
    epoch: int,
) -> StakeSnapshot:
    source_path = _build_stakes_source_path(epoch)

    _ensure_stakes_source_file(
        source_path=source_path,
        vote_account_pubkey=vote_account_pubkey,
    )

    payload, raw_text = _load_stakes_payload(source_path)

    existing_snapshot = _get_existing_snapshot(
        db,
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
    )
    if existing_snapshot is not None:
        _delete_existing_snapshot(
            db,
            snapshot_id=existing_snapshot.id,
        )

    values = StakeSnapshotValues(
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
        source_path=source_path,
        raw_text=raw_text,
        records_count=len(payload),
    )
    snapshot = _create_snapshot(db, values=values)

    _create_stake_accounts(
        db,
        snapshot_id=snapshot.id,
        payload=payload,
    )

    return snapshot
