from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.db import get_db
from app.dependencies import get_current_validator_identity, require_validator
from app.models.reward_policy import RewardPolicy
from app.models.user import User
from app.schemas.examples import POLICY_REQUEST_EXAMPLES
from app.schemas.policy import (
    RewardPolicyCreate,
    RewardPolicyRead,
    RewardPolicyUpdate,
)

router = APIRouter(tags=["policies"])


@router.post(
    "/validators/me/policies",
    response_model=RewardPolicyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create reward policy",
    description=(
        "Creates a reward policy for the authenticated validator. "
        "A policy can be either individual for a specific staker or "
        "default for all unmatched stakers."
    ),
    response_description="Created reward policy.",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": POLICY_REQUEST_EXAMPLES,
                }
            }
        }
    },
)
def create_policy(
    payload: RewardPolicyCreate,
    db: Session = Depends(get_db),
    validator_identity_pubkey: str = Depends(get_current_validator_identity),
) -> RewardPolicy:
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


@router.get(
    "/validators/me/policies",
    response_model=list[RewardPolicyRead],
    summary="List reward policies",
    description="Returns reward policies belonging to the authenticated validator.",
    response_description="List of validator reward policies.",
)
def list_policies(
    db: Session = Depends(get_db),
    validator_identity_pubkey: str = Depends(get_current_validator_identity),
) -> list[RewardPolicy]:
    return (
        db.query(RewardPolicy)
        .filter(RewardPolicy.validator_identity_pubkey == validator_identity_pubkey)
        .filter(RewardPolicy.cluster == settings.app_cluster)
        .order_by(RewardPolicy.created_at.desc())
        .all()
    )


@router.put(
    "/validators/me/policies/{policy_id}",
    response_model=RewardPolicyRead,
    summary="Update reward policy",
    description=(
        "Updates an existing reward policy of the authenticated validator. "
        "The policy can be switched between default and staker-specific modes, "
        "activated or deactivated, and limited to an epoch range."
    ),
    response_description="Updated reward policy.",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": POLICY_REQUEST_EXAMPLES,
                }
            }
        }
    },
)
def update_policy(
    policy_id: int,
    payload: RewardPolicyUpdate,
    db: Session = Depends(get_db),
    validator_identity_pubkey: str = Depends(get_current_validator_identity),
) -> RewardPolicy:
    policy = (
        db.query(RewardPolicy)
        .filter(RewardPolicy.id == policy_id)
        .filter(RewardPolicy.validator_identity_pubkey == validator_identity_pubkey)
        .filter(RewardPolicy.cluster == settings.app_cluster)
        .first()
    )
    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reward policy not found",
        )

    policy.staker_withdrawer_pubkey = payload.staker_withdrawer_pubkey
    policy.is_default = payload.is_default
    policy.mev_bps_back = payload.mev_bps_back
    policy.block_rewards_bps_back = payload.block_rewards_bps_back
    policy.valid_from_epoch = payload.valid_from_epoch
    policy.valid_to_epoch = payload.valid_to_epoch
    policy.is_active = payload.is_active

    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy
