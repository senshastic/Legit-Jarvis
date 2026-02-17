import discord
from discord.ext import commands
from discord import app_commands
from utils import TeamUpAPI, format_event_embed, format_upcoming_events_embed, format_week_events_embed
from roster_storage import RosterStorage


class CalendarCommands(commands.Cog):
    """Commands for viewing calendar events"""

    def __init__(self, bot):
        self.bot = bot
        self.roster_storage = RosterStorage()

    def _get_event_types(self, events, teamup):
        """Get event type mapping for events"""
        event_types = {}
        for event in events:
            subcal_ids = event.get('subcalendar_ids', event.get('subcalendar_id'))
            if subcal_ids:
                event_types[event['id']] = teamup.get_subcalendar_name(subcal_ids)
        return event_types

    def _get_rosters(self, events):
        """Get roster mapping for events based on event titles (team names)"""
        rosters = {}
        for event in events:
            team_name = event.get('title', '').strip()
            if team_name:
                roster = self.roster_storage.get_roster(team_name)
                if roster:
                    rosters[event['id']] = roster
        return rosters

    @app_commands.command(name='upcoming', description='List upcoming scrims from the calendar')
    async def upcoming_scrims(self, interaction: discord.Interaction):
        """List upcoming scrims from the calendar"""
        teamup = TeamUpAPI()
        events = teamup.get_upcoming_events(days=7)

        if not events:
            await interaction.response.send_message("📅 No upcoming scrims scheduled!")
            return

        event_types = self._get_event_types(events, teamup)
        rosters = self._get_rosters(events)
        embed = format_upcoming_events_embed(events, event_types, rosters)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Error formatting events")

    @app_commands.command(name='next', description='Show details of the next scheduled event')
    async def next_event(self, interaction: discord.Interaction):
        """Show details of the next scheduled event"""
        teamup = TeamUpAPI()
        events = teamup.get_upcoming_events(days=14)

        if not events:
            await interaction.response.send_message("📅 No events scheduled!")
            return

        # Sort and get the next event
        events.sort(key=lambda x: x['start_dt'])
        next_event = events[0]

        # Get event type
        subcal_ids = next_event.get('subcalendar_ids', next_event.get('subcalendar_id'))
        event_type = teamup.get_subcalendar_name(subcal_ids) if subcal_ids else None

        # Get roster based on event title (team name)
        team_name = next_event.get('title', '').strip()
        roster = self.roster_storage.get_roster(team_name) if team_name else None

        embed = format_event_embed(next_event, roster=roster, event_type=event_type)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='nextscrim', description='Show details of the next scheduled scrim')
    async def next_scrim(self, interaction: discord.Interaction):
        """Show details of the next scheduled scrim"""
        teamup = TeamUpAPI()
        events = teamup.get_upcoming_events(days=14)

        if not events:
            await interaction.response.send_message("📅 No events scheduled!")
            return

        # Filter for scrims only
        scrim_events = []
        for event in events:
            subcal_ids = event.get('subcalendar_ids', event.get('subcalendar_id'))
            event_type = teamup.get_subcalendar_name(subcal_ids) if subcal_ids else None
            if event_type and 'scrim' in event_type.lower():
                scrim_events.append(event)

        if not scrim_events:
            await interaction.response.send_message("📅 No scrims scheduled!")
            return

        # Sort and get the next scrim
        scrim_events.sort(key=lambda x: x['start_dt'])
        next_event = scrim_events[0]

        # Get event type and roster
        subcal_ids = next_event.get('subcalendar_ids', next_event.get('subcalendar_id'))
        event_type = teamup.get_subcalendar_name(subcal_ids) if subcal_ids else None
        team_name = next_event.get('title', '').strip()
        roster = self.roster_storage.get_roster(team_name) if team_name else None

        embed = format_event_embed(next_event, roster=roster, event_type=event_type)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='nextofficial', description='Show details of the next official match')
    async def next_official(self, interaction: discord.Interaction):
        """Show details of the next official match"""
        teamup = TeamUpAPI()
        events = teamup.get_upcoming_events(days=14)

        if not events:
            await interaction.response.send_message("📅 No events scheduled!")
            return

        # Filter for official matches only
        official_events = []
        for event in events:
            subcal_ids = event.get('subcalendar_ids', event.get('subcalendar_id'))
            event_type = teamup.get_subcalendar_name(subcal_ids) if subcal_ids else None
            if event_type and 'official' in event_type.lower():
                official_events.append(event)

        if not official_events:
            await interaction.response.send_message("📅 No official matches scheduled!")
            return

        # Sort and get the next official match
        official_events.sort(key=lambda x: x['start_dt'])
        next_event = official_events[0]

        # Get event type and roster
        subcal_ids = next_event.get('subcalendar_ids', next_event.get('subcalendar_id'))
        event_type = teamup.get_subcalendar_name(subcal_ids) if subcal_ids else None
        team_name = next_event.get('title', '').strip()
        roster = self.roster_storage.get_roster(team_name) if team_name else None

        embed = format_event_embed(next_event, roster=roster, event_type=event_type)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='scrim', description='Show details of a specific scrim by event ID')
    @app_commands.describe(event_id='The event ID from the calendar')
    async def scrim_details(self, interaction: discord.Interaction, event_id: str):
        """Show details of a specific scrim by event ID"""
        teamup = TeamUpAPI()
        event = teamup.get_event(event_id)

        if not event:
            await interaction.response.send_message(f"❌ Could not find event with ID: {event_id}")
            return

        # Get event type
        subcal_ids = event.get('subcalendar_ids', event.get('subcalendar_id'))
        event_type = teamup.get_subcalendar_name(subcal_ids) if subcal_ids else None

        # Get roster based on event title (team name)
        team_name = event.get('title', '').strip()
        roster = self.roster_storage.get_roster(team_name) if team_name else None

        embed = format_event_embed(event, roster=roster, event_type=event_type)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='today', description='Show events scheduled for today only')
    async def today_scrims(self, interaction: discord.Interaction):
        """Show events scheduled for today"""
        from datetime import datetime

        teamup = TeamUpAPI()
        today = datetime.now().strftime('%Y-%m-%d')

        # Get events for today only (start and end on same day)
        events = teamup.get_events(start_date=today, end_date=today)

        if not events:
            await interaction.response.send_message("📅 No events scheduled for today!")
            return

        event_types = self._get_event_types(events, teamup)
        rosters = self._get_rosters(events)
        embed = format_upcoming_events_embed(events, event_types, rosters)
        embed.title = "📋 Today's Events"
        embed.description = f"{len(events)} event{'s' if len(events) > 1 else ''} scheduled"

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='week', description='Show scrims scheduled for this week')
    async def week_scrims(self, interaction: discord.Interaction):
        """Show scrims scheduled for this week"""
        teamup = TeamUpAPI()
        events = teamup.get_upcoming_events(days=7)

        if not events:
            await interaction.response.send_message("📅 No scrims scheduled this week!")
            return

        event_types = self._get_event_types(events, teamup)
        rosters = self._get_rosters(events)
        embed = format_week_events_embed(events, event_types, rosters)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(CalendarCommands(bot))
