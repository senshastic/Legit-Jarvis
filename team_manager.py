"""
Team configuration management.

Each team maps to one Discord guild and one calendar (TeamUp or Google Calendar).
Config is stored in teams.json; secrets (API keys, credential paths) stay in .env
and are referenced by env-var name inside the JSON.
"""
import json
import os
from typing import Optional

from calendar_provider import CalendarProvider


class TeamConfig:
    def __init__(self, data: dict):
        self.team_id:           str = data['team_id']
        self.name:              str = data['name']
        self.guild_id:          int = int(data['guild_id'])
        self.calendar_type:     str = data['calendar_type']   # "teamup" | "google"
        self.reminder_channel_id:  Optional[int] = int(data['reminder_channel_id']) if data.get('reminder_channel_id') else None
        self.player_role_id:    int = int(data['player_role_id']) if data.get('player_role_id') else 0
        self.coach_role_id:     int = int(data['coach_role_id']) if data.get('coach_role_id') else 0
        self.management_role_id: int = int(data['management_role_id']) if data.get('management_role_id') else 0

        # TeamUp-specific
        self.teamup_calendar_id: Optional[str] = data.get('teamup_calendar_id')
        # API key can be stored directly or referenced via an env-var name
        self.teamup_api_key: Optional[str] = (
            os.getenv(data['teamup_api_key_env'])
            if data.get('teamup_api_key_env')
            else data.get('teamup_api_key')
        )

        # Google Calendar-specific
        self.google_calendar_id: Optional[str] = data.get('google_calendar_id')
        self.google_credentials_file: Optional[str] = (
            os.getenv(data['google_credentials_file_env'])
            if data.get('google_credentials_file_env')
            else data.get('google_credentials_file')
        )

        self.timezone: Optional[str] = data.get('timezone')  # e.g. "America/New_York"

        self._calendar: Optional[CalendarProvider] = None

    def get_calendar(self) -> CalendarProvider:
        """Return the calendar provider for this team (lazily initialized)."""
        if self._calendar is None:
            if self.calendar_type == 'teamup':
                from teamup_api import TeamUpAPI
                self._calendar = TeamUpAPI(self.teamup_calendar_id, self.teamup_api_key)
            elif self.calendar_type == 'google':
                from google_calendar_api import GoogleCalendarAPI
                self._calendar = GoogleCalendarAPI(
                    self.google_calendar_id, self.google_credentials_file
                )
            else:
                raise ValueError(f"Unknown calendar_type '{self.calendar_type}' for team {self.team_id}")
        return self._calendar

    def is_configured(self) -> bool:
        if self.calendar_type == 'teamup':
            return bool(self.teamup_calendar_id and self.teamup_api_key)
        if self.calendar_type == 'google':
            return bool(self.google_calendar_id and self.google_credentials_file)
        return False


class TeamManager:
    """Loads all team configs from teams.json and provides guild → team lookups."""

    def __init__(self, config_path: str = 'teams.json'):
        self._teams:     list[TeamConfig]     = []
        self._guild_map: dict[int, TeamConfig] = {}
        self._config_path = config_path
        self._load()

    def _load(self):
        if not os.path.exists(self._config_path):
            print(f"⚠️  {self._config_path} not found — no teams configured.")
            return
        with open(self._config_path) as f:
            data = json.load(f)
        for entry in data.get('teams', []):
            team = TeamConfig(entry)
            self._teams.append(team)
            self._guild_map[team.guild_id] = team
        print(f"✅ Loaded {len(self._teams)} team(s) from {self._config_path}")

    def get_team_for_guild(self, guild_id: int) -> Optional[TeamConfig]:
        return self._guild_map.get(guild_id)

    def get_all_teams(self) -> list[TeamConfig]:
        return list(self._teams)

    def update_reminder_channel(self, guild_id: int, channel_id: int) -> bool:
        """Persist a new reminder_channel_id for a guild in teams.json."""
        team = self.get_team_for_guild(guild_id)
        if not team:
            return False
        team.reminder_channel_id = channel_id

        if not os.path.exists(self._config_path):
            return False
        with open(self._config_path) as f:
            data = json.load(f)
        for entry in data.get('teams', []):
            if int(entry['guild_id']) == guild_id:
                entry['reminder_channel_id'] = channel_id
                break
        with open(self._config_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
