from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.db import get_db
from app.dependencies import require_validator
from app.models.reward_policy import RewardPolicy
from app.models.user import User
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
                    "examples": {
                        "default_policy": {
                            "summary": "Default policy",
                            "value": {
                                "staker_withdrawer_pubkey": None,
                                "is_default": True,
                                "mev_bps_back": 10000,
                                "block_rewards_bps_back": 5000,
                                "valid_from_epoch": None,
                                "valid_to_epoch": None,
                                "is_active": True,
                            },
                        },
                        "individual_policy": {
                            "summary": "Individual staker policy",
                            "value": {
                                "staker_withdrawer_pubkey": "Staker1111111111111111111111111111111111111",
                                "is_default": False,
                                "mev_bps_back": 10000,
                                "block_rewards_bps_back": 5000,
                                "valid_from_epoch": None,
                                "valid_to_epoch": None,
                                "is_active": True,
                            },
                        },
                    }
                }
            }
        }
    },
)
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


@router.get(
    "/validators/me/policies",
    response_model=list[RewardPolicyRead],
    summary="List reward policies",
    description="Returns reward policies belonging to the authenticated validator.",
    response_description="List of validator reward policies.",
)
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
                    "examples": {
                        "default_policy": {
                            "summary": "Default policy",
                            "value": {
                                "staker_withdrawer_pubkey": None,
                                "is_default": True,
                                "mev_bps_back": 10000,
                                "block_rewards_bps_back": 5000,
                                "valid_from_epoch": None,
                                "valid_to_epoch": None,
                                "is_active": True,
                            },
                        },
                        "individual_policy": {
                            "summary": "Individual staker policy",
                            "value": {
                                "staker_withdrawer_pubkey": "Staker1111111111111111111111111111111111111",
                                "is_default": False,
                                "mev_bps_back": 10000,
                                "block_rewards_bps_back": 5000,
                                "valid_from_epoch": None,
                                "valid_to_epoch": None,
                                "is_active": True,
                            },
                        },
                    }
                }
            }
        }
    },
)
def update_policy(
    policy_id: int,
    payload: RewardPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
) -> RewardPolicy:
    validator_identity_pubkey = current_user.validator_identity_pubkey
    if not validator_identity_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator profile not found",
        )

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
