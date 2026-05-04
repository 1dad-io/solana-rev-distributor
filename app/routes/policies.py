from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.db import get_db
from app.dependencies import require_validator
from app.models.reward_policy import RewardPolicy
from app.models.user import User
from app.schemas.policy import RewardPolicyCreate, RewardPolicyRead

router = APIRouter(prefix="/validators/me/policies", tags=["policies"])


@router.post("", response_model=RewardPolicyRead, status_code=status.HTTP_201_CREATED)
def create_policy(
    payload: RewardPolicyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
) -> RewardPolicy:
    validator_identity_pubkey = current_user.validator_identity_pubkey
    if not validator_identity_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator profile not found",
        )

    policy = RewardPolicy(
        validator_identity_pubkey=validator_identity_pubkey,
        cluster=settings.app_cluster,
        staker_withdrawer_pubkey=payload.staker_withdrawer_pubkey,
        is_default=payload.is_default,
        mev_bps_back=payload.mev_bps_back,
        block_rewards_bps_back=payload.block_rewards_bps_back,
        valid_from_epoch=payload.valid_from_epoch,
        valid_to_epoch=payload.valid_to_epoch,
        is_active=payload.is_active,
    )

    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


@router.get("", response_model=list[RewardPolicyRead])
def list_policies(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
) -> list[RewardPolicy]:
    validator_identity_pubkey = current_user.validator_identity_pubkey
    if not validator_identity_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator profile not found",
        )

    return (
        db.query(RewardPolicy)
        .filter(RewardPolicy.validator_identity_pubkey == validator_identity_pubkey)
        .filter(RewardPolicy.cluster == settings.app_cluster)
        .order_by(RewardPolicy.created_at.desc())
        .all()
    )
