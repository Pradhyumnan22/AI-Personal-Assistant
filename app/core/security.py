"""Simple API-key boundary, replaceable with user authentication later."""

import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.core.config import settings


def verify_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    if settings.api_key and (
        x_api_key is None or not secrets.compare_digest(x_api_key, settings.api_key)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )
