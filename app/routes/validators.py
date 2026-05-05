from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.db import get_db
from app.dependencies import require_validator
from app.models.user import User
from app.models.validator import Validator
from app.schemas.user import ValidatorMeRead, ValidatorMeUpdate
from app.schemas.validator import ValidatorCreate, ValidatorRead

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
    db: Session,
    current_user: User,
) -> ValidatorMeRead:
    validator_identity_pubkey = current_user.validator_identity_pubkey
    if not validator_identity_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator profile not found",
        )

    validator_record = (
        db.query(Validator)
        .filter(Validator.identity_pubkey == validator_identity_pubkey)
        .filter(Validator.cluster == settings.app_cluster)
        .first()
    )

    vote_account_pubkey = None if validator_record is None else validator_record.vote_account_pubkey

    return ValidatorMeRead(
        username=current_user.username,
        role=current_user.role,
        alias=current_user.alias,
        validator_identity_pubkey=current_user.validator_identity_pubkey,
        vote_account_pubkey=vote_account_pubkey,
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
) -> ValidatorMeRead:
    return _build_validator_me_response(db=db, current_user=current_user)


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
) -> ValidatorMeRead:
    if payload.alias is not None:
        current_user.alias = payload.alias
    if payload.is_active is not None:
        current_user.is_active = payload.is_active

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return _build_validator_me_response(db=db, current_user=current_user)
