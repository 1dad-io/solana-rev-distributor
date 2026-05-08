from fastapi import HTTPException, status


def raise_not_found(detail: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def raise_unprocessable(detail: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=detail,
    )


def raise_service_http_exception(exc: Exception) -> None:
    if isinstance(exc, FileNotFoundError):
        raise_not_found(str(exc))

    if isinstance(exc, ValueError):
        raise_unprocessable(str(exc))

    raise exc
