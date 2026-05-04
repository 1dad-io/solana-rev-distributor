from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.db import get_db
from app.dependencies import require_validator
from app.models.epoch_reward_context import EpochRewardContext
from app.models.user import User
from app.schemas.epoch import EpochImportRequest, EpochRewardContextRead
from app.services.epoch_import_service import import_epoch_reward_context

router = APIRouter(prefix="/validators/me/epochs", tags=["epochs"])


@router.post("/import", response_model=EpochRewardContextRead, status_code=status.HTTP_201_CREATED)
def import_epoch_context(
    payload: EpochImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
) -> EpochRewardContext:
    validator_identity_pubkey = current_user.validator_identity_pubkey
    if not validator_identity_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator profile not found",
        )

    try:
        return import_epoch_reward_context(
            db=db,
            validator_identity_pubkey=validator_identity_pubkey,
            epoch=payload.epoch,
            block_rewards_lamports=payload.block_rewards_lamports,
            uptime_bps=payload.uptime_bps,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Validator rewards file not found: {exc}",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/{epoch}", response_model=EpochRewardContextRead)
def get_epoch_context(
    epoch: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
) -> EpochRewardContext:
    validator_identity_pubkey = current_user.validator_identity_pubkey
    if not validator_identity_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator profile not found",
        )

    context = (
        db.query(EpochRewardContext)
        .filter(EpochRewardContext.validator_identity_pubkey == validator_identity_pubkey)
        .filter(EpochRewardContext.cluster == settings.app_cluster)
        .filter(EpochRewardContext.epoch == epoch)
        .first()
    )
    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Epoch reward context not found",
        )

    return context
