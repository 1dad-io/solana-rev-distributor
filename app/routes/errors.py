from typing import NoReturn

from fastapi import HTTPException, status


def raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def raise_unprocessable(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=detail,
    )


def raise_service_http_exception(exc: Exception) -> NoReturn:
    if isinstance(exc, FileNotFoundError):
        raise_not_found(str(exc))

    if isinstance(exc, ValueError):
        raise_unprocessable(str(exc))

    raise exc
