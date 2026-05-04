from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from app.db import get_db
from app.dependencies import require_staker
from app.models.user import User
from app.schemas.user import StakerMeRead, StakerMeUpdate

router = APIRouter(prefix="/stakers", tags=["stakers"])


@router.get("/me", response_model=StakerMeRead)
def get_staker_me(current_user: User = Depends(require_staker)) -> User:
    return current_user


@router.put("/me", response_model=StakerMeRead)
def update_staker_me(
    payload: StakerMeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staker),
) -> User:
    if payload.alias is not None:
        current_user.alias = payload.alias
    if payload.is_active is not None:
        current_user.is_active = payload.is_active

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
