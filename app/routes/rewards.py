from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.db import get_db
from app.dependencies import (
    get_current_active_validator_identity,
    get_current_validator_identity,
    require_active_validator,
    require_staker,
    require_validator,
)
from app.models.reward import Reward
from app.models.user import User
from app.schemas.reward import RewardCalculationRequest, RewardRead, StakerStatsRead
from app.services.epoch_service import resolve_epoch_for_username
from app.services.reward_calculation_service import calculate_rewards_for_epoch

router = APIRouter(tags=["rewards"])


@router.post(
    "/validators/me/rewards/calculate",
    response_model=list[RewardRead],
    status_code=status.HTTP_201_CREATED,
    summary="Calculate rewards",
    description=(
        "Calculates validator reward distribution for the selected epoch. "
        "If epoch is omitted, the service resolves a default epoch "
        "depending on the current user mode. "
        "Reward policy selection is deterministic: only active policies are considered, "
        "the policy must match the epoch range, an individual policy for the staker "
        "takes priority over a default policy, and if multiple matching policies of the "
        "same class exist, the most recently updated policy is used, then the highest id "
        "as a final tiebreaker. "
        "If no matching policy exists for a stake account, the reward row is still created "
        "with status error_no_policy."
    ),
    response_description="Calculated reward rows for the epoch.",
)
def calculate_rewards(
    payload: RewardCalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_validator),
    validator_identity_pubkey: str = Depends(get_current_active_validator_identity),
) -> list[Reward]:
    try:
        resolved_epoch = resolve_epoch_for_username(
            payload.epoch,
            current_user.username,
        )
        return calculate_rewards_for_epoch(
            db=db,
            validator_identity_pubkey=validator_identity_pubkey,
            epoch=resolved_epoch,
            force_recalculate=payload.force_recalculate,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/validators/me/rewards",
    response_model=list[RewardRead],
    summary="List validator rewards",
    description=(
        "Returns calculated reward rows for the authenticated validator "
        "and selected epoch."
    ),
    response_description="List of validator reward rows.",
)
def list_validator_rewards(
    epoch: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
    validator_identity_pubkey: str = Depends(get_current_validator_identity),
) -> list[Reward]:
    resolved_epoch = resolve_epoch_for_username(epoch, current_user.username)

    return (
        db.query(Reward)
        .filter(Reward.validator_identity_pubkey == validator_identity_pubkey)
        .filter(Reward.cluster == settings.app_cluster)
        .filter(Reward.epoch == resolved_epoch)
        .order_by(Reward.id.asc())
        .all()
    )


@router.get(
    "/stakers/me/rewards",
    response_model=list[RewardRead],
    summary="List staker rewards",
    description=(
        "Returns calculated reward rows for the authenticated staker "
        "and selected epoch."
    ),
    response_description="List of staker reward rows.",
)
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

    resolved_epoch = resolve_epoch_for_username(epoch, current_user.username)

    return (
        db.query(Reward)
        .filter(Reward.staker_withdrawer_pubkey == staker_withdrawer_pubkey)
        .filter(Reward.cluster == settings.app_cluster)
        .filter(Reward.epoch == resolved_epoch)
        .order_by(Reward.id.asc())
        .all()
    )


@router.get(
    "/stakers/me/stats",
    response_model=StakerStatsRead,
    summary="Get staker reward stats",
    description=(
        "Returns aggregated reward statistics for the authenticated staker "
        "and selected epoch."
    ),
    response_description="Aggregated staker reward statistics.",
)
def get_staker_stats(
    epoch: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staker),
) -> StakerStatsRead:
    staker_withdrawer_pubkey = current_user.staker_withdrawer_pubkey
    if not staker_withdrawer_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staker profile not found",
        )

    resolved_epoch = resolve_epoch_for_username(epoch, current_user.username)

    rewards = (
        db.query(Reward)
        .filter(Reward.staker_withdrawer_pubkey == staker_withdrawer_pubkey)
        .filter(Reward.cluster == settings.app_cluster)
        .filter(Reward.epoch == resolved_epoch)
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
