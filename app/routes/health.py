from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/")
def read_root() -> dict[str, str]:
    return {"message": f"{settings.app_name} is running"}


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
