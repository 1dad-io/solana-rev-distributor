from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.db import get_db
from app.dependencies import get_current_validator_record, require_validator
from app.models.user import User
from app.models.validator import Validator
from app.schemas.user import ValidatorMeRead, ValidatorMeUpdate
from app.schemas.validator import ValidatorCreate, ValidatorRead
from app.services.profile import apply_self_profile_updates, save_user_profile

router = APIRouter(prefix="/validators", tags=["validators"])


@router.post(
    "",
    response_model=ValidatorRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_validator(payload: ValidatorCreate, db: Session = Depends(get_db)) -> Validator:
    validator = Validator(
        identity_pubkey=payload.identity_pubkey,
        vote_account_pubkey=payload.vote_account_pubkey,
        alias=payload.alias,
        cluster=payload.cluster,
        is_active=payload.is_active,
    )

    db.add(validator)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Validator with the same cluster identity or vote account already exists",
        ) from exc

    db.refresh(validator)
    return validator


@router.get(
    "",
    response_model=list[ValidatorRead],
    include_in_schema=False,
)
def list_validators(db: Session = Depends(get_db)) -> list[Validator]:
    return db.query(Validator).order_by(Validator.created_at.desc()).all()


def _build_validator_me_response(
    current_user: User,
    validator: Validator,
) -> ValidatorMeRead:
    return ValidatorMeRead(
        username=current_user.username,
        role=current_user.role,
        alias=current_user.alias,
        validator_identity_pubkey=current_user.validator_identity_pubkey,
        vote_account_pubkey=validator.vote_account_pubkey,
        is_active=current_user.is_active,
    )


@router.get(
    "/me",
    response_model=ValidatorMeRead,
    summary="Get current validator profile",
    description="Returns the authenticated validator user profile.",
    response_description="Current validator profile.",
)
def get_validator_me(
    current_user: User = Depends(require_validator),
    validator: Validator = Depends(get_current_validator_record),
) -> ValidatorMeRead:
    return _build_validator_me_response(current_user=current_user, validator=validator)


@router.put(
    "/me",
    response_model=ValidatorMeRead,
    summary="Update current validator profile",
    description="Updates editable fields of the authenticated validator profile.",
    response_description="Updated validator profile.",
)
def update_validator_me(
    payload: ValidatorMeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
    validator: Validator = Depends(get_current_validator_record),
) -> ValidatorMeRead:
    apply_self_profile_updates(
        user=current_user,
        alias=payload.alias,
        is_active=payload.is_active,
    )
    save_user_profile(db, current_user)

    return _build_validator_me_response(current_user=current_user, validator=validator)
