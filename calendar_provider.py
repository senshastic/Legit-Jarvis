"""
Abstract base class for calendar providers.
Both TeamUp and Google Calendar implement this interface.
"""
from abc import ABC, abstractmethod


class CalendarProvider(ABC):
    """Common interface for all calendar backends."""

    @abstractmethod
    def get_events(self, start_date=None, end_date=None) -> list:
        """Fetch events between start_date and end_date (YYYY-MM-DD strings)."""
        pass

    @abstractmethod
    def get_event(self, event_id) -> dict:
        """Fetch a single event by its ID. Returns None if not found."""
        pass

    @abstractmethod
    def get_upcoming_events(self, days=7) -> list:
        """Fetch events for the next N days."""
        pass

    @abstractmethod
    def get_event_type(self, event) -> str:
        """
        Return a human-readable event type string for the given event.
        e.g. 'Scrim', 'Official', 'Warmup', 'VOD', or None.
        """
        pass
