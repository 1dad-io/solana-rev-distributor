from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status

from app.db import get_db
from app.models.validator import Validator
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
