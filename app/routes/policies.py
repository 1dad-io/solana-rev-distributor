from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.db import get_db
from app.dependencies import (
    get_current_active_validator_identity,
    get_current_validator_identity,
)
from app.models.reward_policy import RewardPolicy
from app.schemas.examples import POLICY_REQUEST_EXAMPLES
from app.schemas.policy import (
    RewardPolicyCreate,
    RewardPolicyRead,
    RewardPolicyUpdate,
)
from app.services.policy_service import find_duplicate_policy

router = APIRouter(tags=["policies"])


@router.post(
    "/validators/me/policies",
    response_model=RewardPolicyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create reward policy",
    description=(
        "Creates a reward policy for the authenticated validator. "
        "A policy can be either individual for a specific staker or "
        "default for all unmatched stakers. "
        "Creating a policy with a payload identical to an existing policy "
        "of the same validator is not allowed."
    ),
    response_description="Created reward policy.",
    responses={
        409: {
            "description": "An identical reward policy already exists.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An identical reward policy already exists",
                    }
                }
            },
        }
    },
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
    validator_identity_pubkey: str = Depends(get_current_active_validator_identity),
) -> RewardPolicy:
    duplicate_policy = find_duplicate_policy(
        db,
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
    if duplicate_policy is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An identical reward policy already exists",
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
        "activated or deactivated, and limited to an epoch range. "
        "Updating a policy so that it becomes identical to another policy "
        "of the same validator is not allowed."
    ),
    response_description="Updated reward policy.",
    responses={
        404: {
            "description": "Reward policy not found.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Reward policy not found",
                    }
                }
            },
        },
        409: {
            "description": "An identical reward policy already exists.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "An identical reward policy already exists",
                    }
                }
            },
        },
    },
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
    validator_identity_pubkey: str = Depends(get_current_active_validator_identity),
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

    duplicate_policy = find_duplicate_policy(
        db,
        validator_identity_pubkey=validator_identity_pubkey,
        cluster=settings.app_cluster,
        staker_withdrawer_pubkey=payload.staker_withdrawer_pubkey,
        is_default=payload.is_default,
        mev_bps_back=payload.mev_bps_back,
        block_rewards_bps_back=payload.block_rewards_bps_back,
        valid_from_epoch=payload.valid_from_epoch,
        valid_to_epoch=payload.valid_to_epoch,
        is_active=payload.is_active,
        exclude_policy_id=policy.id,
    )
    if duplicate_policy is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An identical reward policy already exists",
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
