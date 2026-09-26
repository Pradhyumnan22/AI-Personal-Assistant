"""Google Calendar API contracts."""

from datetime import datetime

from pydantic import BaseModel, Field


class CalendarStatus(BaseModel):
    configured: bool
    connected: bool


class CalendarConnectResponse(BaseModel):
    authorization_url: str


class CalendarEventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    start: datetime
    end: datetime | None = None
    description: str | None = Field(default=None, max_length=5000)


class CalendarEventResponse(BaseModel):
    id: str
    title: str
    start: str
    end: str
    html_link: str | None = None
