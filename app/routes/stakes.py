from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.config import settings
from app.db import get_db
from app.dependencies import (
    get_current_validator_identity,
    get_current_validator_record,
    require_validator,
)
from app.models.stake_account import StakeAccount
from app.models.stake_snapshot import StakeSnapshot
from app.models.user import User
from app.models.validator import Validator
from app.schemas.stake import StakeAccountRead, StakeImportRequest, StakeSnapshotRead
from app.services.epoch_service import resolve_epoch_for_username
from app.services.stake_import_service import import_stake_snapshot

router = APIRouter(prefix="/validators/me/stakes", tags=["stakes"])


@router.post(
    "/import",
    response_model=StakeSnapshotRead,
    status_code=status.HTTP_201_CREATED,
    summary="Import stake snapshot",
    description=(
        "Imports validator stake snapshot for an epoch. "
        "If the source JSON file is missing, the service attempts to fetch "
        "stake data via Solana CLI."
    ),
    response_description="Imported stake snapshot metadata.",
)
def import_stakes(
    payload: StakeImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
    validator: Validator = Depends(get_current_validator_record),
) -> StakeSnapshot:
    try:
        resolved_epoch = resolve_epoch_for_username(
            payload.epoch,
            current_user.username,
        )
        return import_stake_snapshot(
            db=db,
            validator_identity_pubkey=validator.identity_pubkey,
            vote_account_pubkey=validator.vote_account_pubkey,
            epoch=resolved_epoch,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "",
    response_model=list[StakeSnapshotRead],
    summary="List imported stake snapshots",
    description="Returns imported stake snapshots for the authenticated validator.",
    response_description="List of imported stake snapshots.",
)
def list_stake_snapshots(
    db: Session = Depends(get_db),
    validator_identity_pubkey: str = Depends(get_current_validator_identity),
) -> list[StakeSnapshot]:
    return (
        db.query(StakeSnapshot)
        .filter(StakeSnapshot.validator_identity_pubkey == validator_identity_pubkey)
        .filter(StakeSnapshot.cluster == settings.app_cluster)
        .order_by(StakeSnapshot.epoch.desc())
        .all()
    )


@router.get(
    "/{epoch}/accounts",
    response_model=list[StakeAccountRead],
    summary="List stake accounts for epoch",
    description=(
        "Returns stake accounts from the imported snapshot for the selected "
        "epoch. Optional filters allow returning only active accounts or "
        "only accounts for a specific withdrawer."
    ),
    response_description="List of imported stake accounts for the epoch.",
)
def list_stake_accounts(
    epoch: int,
    active_only: bool = Query(default=False),
    withdrawer: str | None = Query(default=None),
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stake snapshot not found",
        )

    query = db.query(StakeAccount).filter(StakeAccount.snapshot_id == snapshot.id)

    if active_only:
        query = query.filter(StakeAccount.active_stake_lamports.is_not(None))
        query = query.filter(StakeAccount.active_stake_lamports > 0)

    if withdrawer:
        query = query.filter(StakeAccount.withdrawer_authority == withdrawer)

    return query.order_by(StakeAccount.stake_pubkey.asc()).all()
