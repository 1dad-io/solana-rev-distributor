from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.db import get_db
from app.dependencies import require_validator
from app.models.user import User
from app.models.validator import Validator
from app.schemas.user import ValidatorMeRead, ValidatorMeUpdate
from app.schemas.validator import ValidatorCreate, ValidatorRead

router = APIRouter(prefix="/validators", tags=["validators"])


@router.post("", response_model=ValidatorRead, status_code=status.HTTP_201_CREATED)
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


@router.get("", response_model=list[ValidatorRead])
def list_validators(db: Session = Depends(get_db)) -> list[Validator]:
    return db.query(Validator).order_by(Validator.created_at.desc()).all()


@router.get("/me", response_model=ValidatorMeRead)
def get_validator_me(current_user: User = Depends(require_validator)) -> User:
    if not current_user.validator_identity_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator profile not found",
        )
    return current_user


@router.put("/me", response_model=ValidatorMeRead)
def update_validator_me(
    payload: ValidatorMeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
) -> User:
    if payload.alias is not None:
        current_user.alias = payload.alias
    if payload.is_active is not None:
        current_user.is_active = payload.is_active

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
