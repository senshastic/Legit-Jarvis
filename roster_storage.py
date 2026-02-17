"""
Roster storage management for team rosters.
Handles saving and loading roster data to/from JSON file.
"""
import json
import os
from typing import Optional, Dict, List

ROSTER_FILE = 'rosters.json'


class RosterStorage:
    """Manages team roster data persistence."""

    def __init__(self, file_path: str = ROSTER_FILE):
        """
        Initialize roster storage.

        Args:
            file_path: Path to the JSON file for storing rosters
        """
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create the roster file if it doesn't exist."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f, indent=2)

    def _load_rosters(self) -> Dict[str, List[str]]:
        """
        Load all rosters from file.

        Returns:
            Dictionary mapping team names to player lists
        """
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_rosters(self, rosters: Dict[str, List[str]]) -> None:
        """
        Save rosters to file.

        Args:
            rosters: Dictionary mapping team names to player lists
        """
        with open(self.file_path, 'w') as f:
            json.dump(rosters, f, indent=2)

    def get_roster(self, team_name: str) -> Optional[List[str]]:
        """
        Get roster for a specific team.

        Args:
            team_name: Name of the team (case-insensitive)

        Returns:
            List of player names or None if team not found
        """
        rosters = self._load_rosters()
        # Case-insensitive lookup
        for team, players in rosters.items():
            if team.lower() == team_name.lower():
                return players
        return None

    def set_roster(self, team_name: str, players: List[str]) -> None:
        """
        Set roster for a team.

        Args:
            team_name: Name of the team
            players: List of player names
        """
        rosters = self._load_rosters()

        # Update or add roster (preserve original casing of team name if exists)
        team_key = team_name
        for existing_team in rosters.keys():
            if existing_team.lower() == team_name.lower():
                team_key = existing_team
                break

        rosters[team_key] = players
        self._save_rosters(rosters)

    def delete_roster(self, team_name: str) -> bool:
        """
        Delete a team's roster.

        Args:
            team_name: Name of the team (case-insensitive)

        Returns:
            True if roster was deleted, False if team not found
        """
        rosters = self._load_rosters()

        # Find and delete (case-insensitive)
        for team in list(rosters.keys()):
            if team.lower() == team_name.lower():
                del rosters[team]
                self._save_rosters(rosters)
                return True

        return False

    def list_all_teams(self) -> List[str]:
        """
        Get list of all teams with rosters.

        Returns:
            List of team names
        """
        rosters = self._load_rosters()
        return sorted(rosters.keys())

    def clear_all_rosters(self) -> None:
        """Delete all rosters."""
        self._save_rosters({})
