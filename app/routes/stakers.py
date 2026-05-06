from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db import get_db
from app.dependencies import require_staker
from app.models.user import User
from app.schemas.user import StakerMeRead, StakerMeUpdate
from app.services.profile_service import apply_self_profile_updates, save_user_profile

router = APIRouter(prefix="/stakers", tags=["stakers"])


@router.get(
    "/me",
    response_model=StakerMeRead,
    summary="Get current staker profile",
    description="Returns the authenticated staker user profile.",
    response_description="Current staker profile.",
)
def get_staker_me(current_user: User = Depends(require_staker)) -> User:
    return current_user


@router.put(
    "/me",
    response_model=StakerMeRead,
    summary="Update current staker profile",
    description="Updates editable fields of the authenticated staker profile.",
    response_description="Updated staker profile.",
)
def update_staker_me(
    payload: StakerMeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staker),
) -> User:
    apply_self_profile_updates(
        user=current_user,
        alias=payload.alias,
        is_active=payload.is_active,
    )
    return save_user_profile(db, current_user)
