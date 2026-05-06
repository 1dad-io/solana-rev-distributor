from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.db import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.validator import Validator
from app.schemas.auth import SignupRequest, TokenResponse
from app.schemas.examples import (
    DEMO_ALIAS_STAKER,
    DEMO_ALIAS_VALIDATOR,
    DEMO_PASSWORD,
    DEMO_STAKER_WITHDRAWER,
    DEMO_USERNAME_STAKER,
    DEMO_USERNAME_VALIDATOR,
    DEMO_VALIDATOR_IDENTITY,
    DEMO_VOTE_ACCOUNT,
)
from app.schemas.user import UserRead
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

SIGNUP_REQUEST_EXAMPLES = {
    "validator": {
        "summary": "Validator signup",
        "value": {
            "username": DEMO_USERNAME_VALIDATOR,
            "password": DEMO_PASSWORD,
            "role": "validator",
            "alias": DEMO_ALIAS_VALIDATOR,
            "validator_identity_pubkey": DEMO_VALIDATOR_IDENTITY,
            "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
            "staker_withdrawer_pubkey": None,
            "is_active": True,
        },
    },
    "staker": {
        "summary": "Staker signup",
        "value": {
            "username": DEMO_USERNAME_STAKER,
            "password": DEMO_PASSWORD,
            "role": "staker",
            "alias": DEMO_ALIAS_STAKER,
            "validator_identity_pubkey": None,
            "vote_account_pubkey": None,
            "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
            "is_active": True,
        },
    },
}


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create user account",
    description=(
        "Registers a new application user. "
        "For validator role, validator_identity_pubkey and vote_account_pubkey "
        "must be provided. For staker role, only staker_withdrawer_pubkey "
        "must be provided."
    ),
    response_description="Created user profile.",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": SIGNUP_REQUEST_EXAMPLES,
                }
            }
        }
    },
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> User:
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
        alias=payload.alias,
        validator_identity_pubkey=payload.validator_identity_pubkey,
        staker_withdrawer_pubkey=payload.staker_withdrawer_pubkey,
        is_active=payload.is_active,
    )
    db.add(user)

    if payload.role == "validator":
        validator = Validator(
            identity_pubkey=payload.validator_identity_pubkey,
            vote_account_pubkey=payload.vote_account_pubkey,
            alias=payload.alias or payload.username,
            cluster=settings.app_cluster,
            is_active=payload.is_active,
        )
        db.add(validator)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "User or validator with the same username or public key "
                "already exists"
            ),
        ) from exc

    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in",
    description=(
        "Authenticates a user with username and password, "
        "then returns a Bearer access token."
    ),
    response_description="Bearer access token.",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = db.query(User).filter(User.username == form_data.username).first()

    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    access_token = create_access_token(subject=user.username)
    return TokenResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
    description="Returns the authenticated user profile for the current access token.",
    response_description="Current authenticated user profile.",
)
def get_auth_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
