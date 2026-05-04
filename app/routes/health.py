from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/")
def read_root() -> dict[str, str]:
    settings = get_settings()
    return {
        "message": f"Welcome to {settings.app_name}",
        "cluster": settings.app_cluster,
    }


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
