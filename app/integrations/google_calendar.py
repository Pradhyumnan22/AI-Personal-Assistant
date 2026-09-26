"""Google Calendar OAuth and API integration."""

from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import CalendarCredential

CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


class CalendarConfigurationError(RuntimeError):
    pass


class GoogleCalendarService:
    def __init__(self, session: Session):
        self.session = session

    @property
    def configured(self) -> bool:
        return bool(settings.google_client_id and settings.google_client_secret)

    @property
    def connected(self) -> bool:
        return self.session.get(CalendarCredential, "primary") is not None

    def _client_config(self) -> dict:
        if not self.configured:
            raise CalendarConfigurationError(
                "Google Calendar OAuth credentials are not configured"
            )
        return {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri],
            }
        }

    def authorization_url(self) -> str:
        flow = Flow.from_client_config(
            self._client_config(),
            scopes=CALENDAR_SCOPES,
            redirect_uri=settings.google_redirect_uri,
        )
        state = URLSafeTimedSerializer(settings.secret_key).dumps(
            {"purpose": "google-calendar"}
        )
        url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=state,
        )
        return url

    def connect(self, code: str, state: str) -> None:
        try:
            payload = URLSafeTimedSerializer(settings.secret_key).loads(
                state, max_age=600
            )
        except (BadSignature, SignatureExpired) as exc:
            raise ValueError("Invalid or expired OAuth state") from exc
        if payload.get("purpose") != "google-calendar":
            raise ValueError("Invalid OAuth state")
        flow = Flow.from_client_config(
            self._client_config(),
            scopes=CALENDAR_SCOPES,
            redirect_uri=settings.google_redirect_uri,
            state=state,
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials
        record = self.session.get(CalendarCredential, "primary")
        if record is None:
            record = CalendarCredential(
                id="primary",
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_uri=credentials.token_uri,
                scopes=" ".join(credentials.scopes or CALENDAR_SCOPES),
                expiry=credentials.expiry,
            )
            self.session.add(record)
        else:
            record.access_token = credentials.token
            record.refresh_token = credentials.refresh_token or record.refresh_token
            record.expiry = credentials.expiry
            record.scopes = " ".join(credentials.scopes or CALENDAR_SCOPES)
        self.session.commit()

    def disconnect(self) -> None:
        record = self.session.get(CalendarCredential, "primary")
        if record:
            self.session.delete(record)
            self.session.commit()

    def _credentials(self) -> Credentials:
        record = self.session.get(CalendarCredential, "primary")
        if record is None:
            raise CalendarConfigurationError("Google Calendar is not connected")
        credentials = Credentials(
            token=record.access_token,
            refresh_token=record.refresh_token,
            token_uri=record.token_uri,
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            scopes=record.scopes.split(),
            expiry=record.expiry,
        )
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            record.access_token = credentials.token
            record.expiry = credentials.expiry
            self.session.commit()
        return credentials

    def _api(self):
        return build(
            "calendar", "v3", credentials=self._credentials(), cache_discovery=False
        )

    def list_events(self, limit: int = 10) -> list[dict]:
        now = datetime.now(timezone.utc).isoformat()
        result = (
            self._api()
            .events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max(1, min(limit, 50)),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return [
            {
                "id": event["id"],
                "title": event.get("summary", "Untitled event"),
                "start": event.get("start", {}).get("dateTime")
                or event.get("start", {}).get("date"),
                "end": event.get("end", {}).get("dateTime")
                or event.get("end", {}).get("date"),
                "html_link": event.get("htmlLink"),
            }
            for event in result.get("items", [])
        ]

    def create_event(
        self,
        title: str,
        start: datetime,
        end: datetime | None = None,
        description: str | None = None,
    ) -> dict:
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        end = end or (start + timedelta(hours=1))
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        event = (
            self._api()
            .events()
            .insert(
                calendarId="primary",
                body={
                    "summary": title,
                    "description": description,
                    "start": {"dateTime": start.isoformat()},
                    "end": {"dateTime": end.isoformat()},
                },
            )
            .execute()
        )
        return {
            "id": event["id"],
            "title": event.get("summary", title),
            "start": event["start"]["dateTime"],
            "end": event["end"]["dateTime"],
            "html_link": event.get("htmlLink"),
        }
