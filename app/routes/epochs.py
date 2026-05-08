from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

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
from app.routes.errors import raise_not_found, raise_service_http_exception
from app.schemas.epoch import EpochImportRequest, EpochRewardContextRead
from app.services.epoch import resolve_epoch_for_username
from app.services.epoch_import import import_epoch_reward_context

router = APIRouter(tags=["epochs"])


@router.post(
    "/validators/me/epochs/import",
    response_model=EpochRewardContextRead,
    status_code=status.HTTP_201_CREATED,
    summary="Import epoch reward context",
    description=(
        "Imports validator reward context for an epoch. "
        "If the source file is missing, the backend attempts to fetch it "
        "from the configured Jito rewards endpoint."
    ),
    response_description="Imported epoch reward context.",
)
def import_epoch_context(
    payload: EpochImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_validator),
    validator_record: Validator = Depends(get_current_active_validator_record),
) -> EpochRewardContext:
    epoch = resolve_epoch_for_username(payload.epoch, current_user.username)

    try:
        return import_epoch_reward_context(
            db,
            validator_identity_pubkey=validator_record.identity_pubkey,
            vote_account_pubkey=validator_record.vote_account_pubkey,
            epoch=epoch,
            block_rewards_lamports=payload.block_rewards_lamports,
            uptime_bps=payload.uptime_bps,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise_service_http_exception(exc)


@router.get(
    "/validators/me/epochs/{epoch}",
    response_model=EpochRewardContextRead,
    summary="Get epoch reward context",
    description="Returns imported reward context for the authenticated validator and epoch.",
    response_description="Epoch reward context.",
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
        raise_not_found("Epoch reward context not found")

    return context
