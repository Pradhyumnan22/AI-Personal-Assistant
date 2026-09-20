"""Root endpoint with basic API information."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.root import RootResponse

router = APIRouter()


@router.get("/", response_model=RootResponse)
def get_api_info() -> RootResponse:
    """Return basic information about the running API."""
    return RootResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        docs="/docs",
    )
