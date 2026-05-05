from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get(
    "/",
    summary="Root endpoint",
    description="Basic root endpoint for quick API availability check.",
    response_description="Simple API status message.",
)
def root() -> dict[str, str]:
    return {"message": "solana-rev-distributor"}


@router.get(
    "/health",
    summary="Health check",
    description="Returns the application health status.",
    response_description="Application health status payload.",
)
def health() -> dict[str, str]:
    return {"status": "ok"}
