"""Google Calendar OAuth and event endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import RedirectResponse

from app.api.dependencies import DatabaseSession
from app.core.config import settings
from app.core.security import verify_api_key
from app.integrations.google_calendar import (
    CalendarConfigurationError,
    GoogleCalendarService,
)
from app.schemas.calendar import (
    CalendarConnectResponse,
    CalendarEventCreate,
    CalendarEventResponse,
    CalendarStatus,
)

router = APIRouter(
    prefix="/api/v1/calendar", dependencies=[Depends(verify_api_key)]
)
oauth_router = APIRouter(prefix="/api/v1/calendar")


@router.get("/status", response_model=CalendarStatus)
def calendar_status(session: DatabaseSession):
    service = GoogleCalendarService(session)
    return CalendarStatus(
        configured=service.configured, connected=service.connected
    )


@router.get("/connect", response_model=CalendarConnectResponse)
def connect_calendar(session: DatabaseSession):
    try:
        return CalendarConnectResponse(
            authorization_url=GoogleCalendarService(session).authorization_url()
        )
    except CalendarConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@oauth_router.get("/callback", include_in_schema=False)
def calendar_callback(
    session: DatabaseSession,
    code: str = Query(...),
    state: str = Query(...),
):
    try:
        GoogleCalendarService(session).connect(code, state)
    except (CalendarConfigurationError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RedirectResponse(f"{settings.frontend_url}?calendar=connected")


@router.delete("/connection", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_calendar(session: DatabaseSession) -> Response:
    GoogleCalendarService(session).disconnect()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/events", response_model=list[CalendarEventResponse])
def list_calendar_events(session: DatabaseSession, limit: int = Query(10, ge=1, le=50)):
    try:
        return GoogleCalendarService(session).list_events(limit)
    except CalendarConfigurationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post(
    "/events",
    response_model=CalendarEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_calendar_event(payload: CalendarEventCreate, session: DatabaseSession):
    try:
        return GoogleCalendarService(session).create_event(
            title=payload.title,
            start=payload.start,
            end=payload.end,
            description=payload.description,
        )
    except CalendarConfigurationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
