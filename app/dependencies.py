from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User
from app.models.validator import Validator
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    username = payload.get("sub")

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return user


def require_validator(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "validator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Validator access required",
        )
    return current_user


def require_active_validator(current_user: User = Depends(require_validator)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def require_staker(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "staker":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staker access required",
        )
    return current_user


def require_active_staker(current_user: User = Depends(require_staker)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def _get_validator_identity_from_user(current_user: User) -> str:
    validator_identity_pubkey = current_user.validator_identity_pubkey
    if not validator_identity_pubkey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator profile not found",
        )
    return validator_identity_pubkey


def get_current_validator_identity(
    current_user: User = Depends(require_validator),
) -> str:
    return _get_validator_identity_from_user(current_user)


def get_current_active_validator_identity(
    current_user: User = Depends(require_active_validator),
) -> str:
    return _get_validator_identity_from_user(current_user)


def _get_validator_record_by_identity(
    db: Session,
    *,
    validator_identity_pubkey: str,
) -> Validator:
    validator = (
        db.query(Validator)
        .filter(Validator.identity_pubkey == validator_identity_pubkey)
        .filter(Validator.cluster == settings.app_cluster)
        .first()
    )
    if validator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validator record not found",
        )
    return validator


def get_current_validator_record(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_validator),
) -> Validator:
    validator_identity_pubkey = _get_validator_identity_from_user(current_user)
    return _get_validator_record_by_identity(
        db,
        validator_identity_pubkey=validator_identity_pubkey,
    )


def get_current_active_validator_record(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_validator),
) -> Validator:
    validator_identity_pubkey = _get_validator_identity_from_user(current_user)
    return _get_validator_record_by_identity(
        db,
        validator_identity_pubkey=validator_identity_pubkey,
    )
