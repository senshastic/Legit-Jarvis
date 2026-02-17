import requests
from datetime import datetime, timedelta
import os


class TeamUpAPI:
    """Handles all TeamUp Calendar API interactions"""

    def __init__(self, calendar_id=None, api_key=None):
        self.calendar_id = calendar_id or os.getenv('TEAMUP_CALENDAR_ID')
        self.api_key = api_key or os.getenv('TEAMUP_API_KEY')
        self.base_url = f"https://api.teamup.com/{self.calendar_id}"
        self.headers = {
            'Teamup-Token': self.api_key
        }
        self.subcalendars = self._fetch_subcalendars()
    
    def get_events(self, start_date=None, end_date=None):
        """Fetch events from TeamUp calendar"""
        if not start_date:
            start_date = datetime.now().strftime('%Y-%m-%d')
        if not end_date:
            end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/events"
        params = {
            'startDate': start_date,
            'endDate': end_date
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get('events', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching events: {e}")
            return []
    
    def get_event(self, event_id):
        """Get a specific event by ID"""
        url = f"{self.base_url}/events/{event_id}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get('event', {})
        except requests.exceptions.RequestException as e:
            print(f"Error fetching event {event_id}: {e}")
            return None
    
    def get_upcoming_events(self, days=7):
        """Get events for the next N days"""
        start = datetime.now().strftime('%Y-%m-%d')
        end = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        return self.get_events(start, end)

    def _fetch_subcalendars(self):
        """Fetch subcalendar information"""
        url = f"{self.base_url}/subcalendars"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            subcals = response.json().get('subcalendars', [])
            # Create a mapping of subcalendar_id to name
            return {str(sub['id']): sub['name'] for sub in subcals}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching subcalendars: {e}")
            return {}

    def get_subcalendar_name(self, subcalendar_id):
        """Get the name of a subcalendar by ID"""
        if isinstance(subcalendar_id, list) and len(subcalendar_id) > 0:
            subcalendar_id = subcalendar_id[0]
        return self.subcalendars.get(str(subcalendar_id), "Unknown")
