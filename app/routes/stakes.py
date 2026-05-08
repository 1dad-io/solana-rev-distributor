from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.dependencies import (
    get_current_active_validator_record,
    get_current_validator_identity,
    require_active_validator,
)
from app.models.stake_account import StakeAccount
from app.models.stake_snapshot import StakeSnapshot
from app.models.user import User
from app.models.validator import Validator
from app.routes.errors import raise_not_found, raise_service_http_exception
from app.schemas.stake import StakeAccountRead, StakeImportRequest, StakeSnapshotRead
from app.services.epoch import resolve_epoch_for_username
from app.services.stake_import import import_stake_snapshot

router = APIRouter(tags=["stakes"])


@router.post(
    "/validators/me/stakes/import",
    response_model=StakeSnapshotRead,
    status_code=status.HTTP_201_CREATED,
    summary="Import stake snapshot",
    description=(
        "Imports validator stake snapshot for an epoch. "
        "If the JSON snapshot is missing, the backend attempts to fetch it "
        "through the Solana CLI."
    ),
    response_description="Imported stake snapshot.",
)
def import_stakes(
    payload: StakeImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_validator),
    validator_record: Validator = Depends(get_current_active_validator_record),
) -> StakeSnapshot:
    epoch = resolve_epoch_for_username(payload.epoch, current_user.username)

    try:
        return import_stake_snapshot(
            db,
            validator_identity_pubkey=validator_record.identity_pubkey,
            vote_account_pubkey=validator_record.vote_account_pubkey,
            epoch=epoch,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise_service_http_exception(exc)


@router.get(
    "/validators/me/stakes",
    response_model=list[StakeSnapshotRead],
    summary="List imported stake snapshots",
    description="Returns stake snapshots for the authenticated validator.",
    response_description="List of stake snapshots.",
)
def list_stake_snapshots(
    db: Session = Depends(get_db),
    validator_identity_pubkey: str = Depends(get_current_validator_identity),
) -> list[StakeSnapshot]:
    return (
        db.query(StakeSnapshot)
        .filter(StakeSnapshot.validator_identity_pubkey == validator_identity_pubkey)
        .filter(StakeSnapshot.cluster == settings.app_cluster)
        .order_by(StakeSnapshot.epoch.desc(), StakeSnapshot.id.desc())
        .all()
    )


@router.get(
    "/validators/me/stakes/{epoch}/accounts",
    response_model=list[StakeAccountRead],
    summary="List imported stake accounts for epoch",
    description="Returns stake accounts from the imported snapshot for the given epoch.",
    response_description="List of stake accounts.",
)
def list_stake_accounts(
    epoch: int,
    db: Session = Depends(get_db),
    validator_identity_pubkey: str = Depends(get_current_validator_identity),
) -> list[StakeAccount]:
    snapshot = (
        db.query(StakeSnapshot)
        .filter(StakeSnapshot.validator_identity_pubkey == validator_identity_pubkey)
        .filter(StakeSnapshot.cluster == settings.app_cluster)
        .filter(StakeSnapshot.epoch == epoch)
        .first()
    )

    if snapshot is None:
        raise_not_found("Stake snapshot not found")

    return (
        db.query(StakeAccount)
        .filter(StakeAccount.snapshot_id == snapshot.id)
        .order_by(StakeAccount.id.asc())
        .all()
    )
