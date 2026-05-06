from sqlalchemy.orm import Session

from app.models.user import User


def apply_self_profile_updates(
    user: User,
    alias: str | None,
    is_active: bool | None,
) -> User:
    if alias is not None:
        user.alias = alias
    if is_active is not None:
        user.is_active = is_active
    return user


def save_user_profile(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
