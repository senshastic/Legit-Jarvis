"""
Google Calendar provider.
Uses a service account for authentication — share your calendar with the
service account email address found in the credentials JSON file.

Required packages: google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build

from calendar_provider import CalendarProvider

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

_TYPE_KEYWORDS = [
    ('Scrim',    ['scrim']),
    ('Official', ['official']),
    ('Warmup',   ['warmup', 'warm up']),
    ('VOD',      ['vod']),
]

# Keywords to strip when extracting the team name from a title
_STRIP_WORDS = ['scrim', 'official', 'warmup', 'warm up', 'vod']


def _infer_event_type(text: str):
    text = text.lower()
    for type_name, keywords in _TYPE_KEYWORDS:
        if any(kw in text for kw in keywords):
            return type_name
    # "vs" without a known keyword → treat as official match
    if ' vs ' in text:
        return 'Official'
    return None


def _parse_team_name(title: str) -> str:
    """
    Extract the team name from a Google Calendar event title.
    e.g. 'SSG Scrim' → 'SSG'
         'SSG Scrim vs TeamX' → 'SSG'
         'SSG Official vs TeamX' → 'SSG'
    """
    name = title
    # Remove "vs ..." suffix first
    lower = name.lower()
    for sep in [' vs ', ' vs.']:
        idx = lower.find(sep)
        if idx != -1:
            name = name[:idx]
            lower = name.lower()
    # Remove event-type words
    for word in _STRIP_WORDS:
        # Case-insensitive word removal (whole word match)
        import re
        name = re.sub(r'(?i)\b' + re.escape(word) + r'\b', '', name)
    return name.strip()


def _parse_opponent(title: str) -> str:
    """Try to extract opponent from titles like 'SSG Scrim vs TeamName'."""
    lower = title.lower()
    for sep in [' vs ', ' vs.']:
        if sep in lower:
            parts = title.split(sep, 1)
            if len(parts) == 2:
                return parts[1].strip()
    return ''


def _normalize(event: dict) -> dict:
    """Convert a raw Google Calendar event to the shared event format."""
    start = event.get('start', {})
    end = event.get('end', {})
    # All-day events use 'date'; timed events use 'dateTime'
    start_dt = start.get('dateTime') or (start.get('date', '') + 'T00:00:00Z')
    end_dt   = end.get('dateTime')   or (end.get('date', '')   + 'T00:00:00Z')

    title = event.get('summary', 'Untitled')
    return {
        'id':        event['id'],
        'title':     title,
        'team_name': _parse_team_name(title),  # cleaned name used for roster lookup
        'start_dt':  start_dt,
        'end_dt':    end_dt,
        'notes':     event.get('description', ''),
        'location':  event.get('location', ''),
        'who':       _parse_opponent(title),
    }


class GoogleCalendarAPI(CalendarProvider):
    """Read-only Google Calendar provider using a service account."""

    def __init__(self, calendar_id: str, credentials_file: str, tz_name: str = None):
        self.calendar_id = calendar_id
        self._tz = ZoneInfo(tz_name) if tz_name else timezone.utc
        creds = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=SCOPES
        )
        self._service = build('calendar', 'v3', credentials=creds)

    def get_events(self, start_date=None, end_date=None) -> list:
        now = datetime.now(timezone.utc)
        if start_date:
            time_min = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=self._tz).isoformat()
        else:
            time_min = now.isoformat()

        if end_date:
            # end of the end_date day — extend to 6am next day for late-night sessions
            time_max = (datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=self._tz)
                        + timedelta(days=1, hours=6)).isoformat()
        else:
            time_max = (now + timedelta(days=7)).isoformat()

        try:
            result = self._service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime',
            ).execute()
            return [_normalize(e) for e in result.get('items', [])]
        except Exception as e:
            print(f"Error fetching Google Calendar events: {e}")
            return []

    def get_event(self, event_id) -> dict:
        try:
            raw = self._service.events().get(
                calendarId=self.calendar_id, eventId=event_id
            ).execute()
            return _normalize(raw)
        except Exception as e:
            print(f"Error fetching Google Calendar event {event_id}: {e}")
            return None

    def get_upcoming_events(self, days=7) -> list:
        start = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        end   = (datetime.now(timezone.utc) + timedelta(days=days)).strftime('%Y-%m-%d')
        return self.get_events(start, end)

    def get_event_type(self, event) -> str:
        title = event.get('title', '')
        notes = event.get('notes', '')
        return _infer_event_type(title + ' ' + notes)

    def append_availability_note(self, event_id, note: str) -> bool:
        """Append an availability note to the Google Calendar event's description."""
        try:
            raw = self._service.events().get(
                calendarId=self.calendar_id, eventId=event_id
            ).execute()
            current_desc = raw.get('description') or ''
            updated_desc = (current_desc.rstrip() + '\n' + note).lstrip()
            self._service.events().patch(
                calendarId=self.calendar_id,
                eventId=event_id,
                body={'description': updated_desc}
            ).execute()
            return True
        except Exception as e:
            print(f"Error updating Google Calendar event {event_id}: {e}")
            return False
