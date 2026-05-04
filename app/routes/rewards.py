from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.db import get_db
from app.dependencies import require_staker, require_validator
from app.models.reward import Reward
from app.models.user import User
from app.schemas.reward import RewardCalculationRequest, RewardRead, StakerStatsRead
from app.services.reward_calculation_service import calculate_rewards_for_epoch

router = APIRouter(tags=["rewards"])


@router.post(
    "/validators/me/rewards/calculate",
    response_model=list[RewardRead],
    status_code=status.HTTP_201_CREATED,
)
def calculate_rewards(
    payload: RewardCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
) -> list[Reward]:
    validator_identity_pubkey = current_user.validator_identity_pubkey
    if not validator_identity_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator profile not found",
        )

    try:
        return calculate_rewards_for_epoch(
            db=db,
            validator_identity_pubkey=validator_identity_pubkey,
            epoch=payload.epoch,
            force_recalculate=payload.force_recalculate,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get("/validators/me/rewards", response_model=list[RewardRead])
def list_validator_rewards(
    epoch: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
) -> list[Reward]:
    validator_identity_pubkey = current_user.validator_identity_pubkey
    if not validator_identity_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator profile not found",
        )

    query = (
        db.query(Reward)
        .filter(Reward.validator_identity_pubkey == validator_identity_pubkey)
        .filter(Reward.cluster == settings.app_cluster)
    )

    if epoch is not None:
        query = query.filter(Reward.epoch == epoch)

    return query.order_by(Reward.epoch.desc(), Reward.id.asc()).all()


@router.get("/stakers/me/rewards", response_model=list[RewardRead])
def list_staker_rewards(
    epoch: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staker),
) -> list[Reward]:
    staker_withdrawer_pubkey = current_user.staker_withdrawer_pubkey
    if not staker_withdrawer_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staker profile not found",
        )

    query = (
        db.query(Reward)
        .filter(Reward.staker_withdrawer_pubkey == staker_withdrawer_pubkey)
        .filter(Reward.cluster == settings.app_cluster)
    )

    if epoch is not None:
        query = query.filter(Reward.epoch == epoch)

    return query.order_by(Reward.epoch.desc(), Reward.id.asc()).all()


@router.get("/stakers/me/stats", response_model=StakerStatsRead)
def get_staker_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staker),
) -> StakerStatsRead:
    staker_withdrawer_pubkey = current_user.staker_withdrawer_pubkey
    if not staker_withdrawer_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staker profile not found",
        )

    rewards = (
        db.query(Reward)
        .filter(Reward.staker_withdrawer_pubkey == staker_withdrawer_pubkey)
        .filter(Reward.cluster == settings.app_cluster)
        .all()
    )

    rewards_count = len(rewards)
    epochs_count = len({reward.epoch for reward in rewards})
    stake_accounts_count = len({reward.stake_pubkey for reward in rewards})
    gross_total_lamports = sum(reward.gross_reward_lamports for reward in rewards)
    payable_total_lamports = sum(reward.payable_reward_lamports for reward in rewards)

    return StakerStatsRead(
        staker_withdrawer_pubkey=staker_withdrawer_pubkey,
        rewards_count=rewards_count,
        epochs_count=epochs_count,
        stake_accounts_count=stake_accounts_count,
        gross_total_lamports=gross_total_lamports,
        payable_total_lamports=payable_total_lamports,
    )
