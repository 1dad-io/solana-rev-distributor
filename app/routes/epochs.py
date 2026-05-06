import httpx
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.db import get_db
from app.dependencies import (
    get_current_active_validator_record,
    get_current_validator_identity,
    require_active_validator,
)
from app.models.epoch_reward_context import EpochRewardContext
from app.models.user import User
from app.models.validator import Validator
from app.schemas.epoch import EpochImportRequest, EpochRewardContextRead
from app.services.epoch_import_service import import_epoch_reward_context
from app.services.epoch_service import resolve_epoch_for_username

router = APIRouter(prefix="/validators/me/epochs", tags=["epochs"])


@router.post(
    "/import",
    response_model=EpochRewardContextRead,
    status_code=status.HTTP_201_CREATED,
    summary="Import epoch reward context",
    description=(
        "Imports epoch reward context for the authenticated validator. "
        "If the source JSON file is missing, the service attempts to fetch "
        "validator rewards from Jito."
    ),
    response_description="Imported epoch reward context.",
)
def import_epoch_context(
    payload: EpochImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_validator),
    validator: Validator = Depends(get_current_active_validator_record),
) -> EpochRewardContext:
    try:
        resolved_epoch = resolve_epoch_for_username(
            payload.epoch,
            current_user.username,
        )
        return import_epoch_reward_context(
            db=db,
            validator_identity_pubkey=validator.identity_pubkey,
            vote_account_pubkey=validator.vote_account_pubkey,
            epoch=resolved_epoch,
            block_rewards_lamports=payload.block_rewards_lamports,
            uptime_bps=payload.uptime_bps,
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
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch Jito validator rewards: {exc}",
        ) from exc


@router.get(
    "/{epoch}",
    response_model=EpochRewardContextRead,
    summary="Get epoch reward context",
    description="Returns the imported epoch reward context for the selected epoch.",
    response_description="Epoch reward context for the selected epoch.",
)
def get_epoch_context(
    epoch: int,
    db: Session = Depends(get_db),
    validator_identity_pubkey: str = Depends(get_current_validator_identity),
) -> EpochRewardContext:
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
