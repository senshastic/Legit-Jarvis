import discord
from discord.ext import commands
from discord import app_commands
from embeds import format_event_embed, format_upcoming_events_embed, format_week_events_embed
from roster_storage import RosterStorage


def _no_team_response(interaction: discord.Interaction):
    return interaction.response.send_message(
        "❌ This server is not configured. Add it to `teams.json`.",
        ephemeral=True
    )


class CalendarCommands(commands.Cog):
    """Commands for viewing calendar events."""

    def __init__(self, bot):
        self.bot = bot
        self.roster_storage = RosterStorage()

    def _get_team(self, interaction: discord.Interaction):
        return self.bot.team_manager.get_team_for_guild(interaction.guild_id)

    def _enrich_events(self, events, calendar):
        """Return (event_types dict, rosters dict) for a list of events."""
        event_types = {}
        rosters = {}
        for event in events:
            event_types[event['id']] = calendar.get_event_type(event)
            team_name = _roster_key(event)
            if team_name:
                roster = self.roster_storage.get_roster(team_name)
                if roster:
                    rosters[event['id']] = roster
        return event_types, rosters

    # ------------------------------------------------------------------

    @app_commands.command(name='upcoming', description='List upcoming scrims from the calendar')
    async def upcoming_scrims(self, interaction: discord.Interaction):
        team = self._get_team(interaction)
        if not team:
            return await _no_team_response(interaction)

        calendar = team.get_calendar()
        events = calendar.get_upcoming_events(days=7)
        if not events:
            return await interaction.response.send_message("📅 No upcoming scrims scheduled!")

        event_types, rosters = self._enrich_events(events, calendar)
        embed = format_upcoming_events_embed(events, event_types, rosters)
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Error formatting events")

    @app_commands.command(name='next', description='Show details of the next scheduled event')
    async def next_event(self, interaction: discord.Interaction):
        team = self._get_team(interaction)
        if not team:
            return await _no_team_response(interaction)

        calendar = team.get_calendar()
        events = calendar.get_upcoming_events(days=14)
        if not events:
            return await interaction.response.send_message("📅 No events scheduled!")

        events.sort(key=lambda x: x['start_dt'])
        event = events[0]
        event_type = calendar.get_event_type(event)
        roster = self.roster_storage.get_roster(_roster_key(event)) or None

        await interaction.response.send_message(
            embed=format_event_embed(event, roster=roster, event_type=event_type)
        )

    @app_commands.command(name='nextscrim', description='Show details of the next scheduled scrim')
    async def next_scrim(self, interaction: discord.Interaction):
        team = self._get_team(interaction)
        if not team:
            return await _no_team_response(interaction)

        calendar = team.get_calendar()
        events = calendar.get_upcoming_events(days=14)
        if not events:
            return await interaction.response.send_message("📅 No events scheduled!")

        scrims = [e for e in events if _is_type(calendar.get_event_type(e), 'scrim')]
        if not scrims:
            return await interaction.response.send_message("📅 No scrims scheduled!")

        scrims.sort(key=lambda x: x['start_dt'])
        event = scrims[0]
        event_type = calendar.get_event_type(event)
        roster = self.roster_storage.get_roster(_roster_key(event)) or None

        await interaction.response.send_message(
            embed=format_event_embed(event, roster=roster, event_type=event_type)
        )

    @app_commands.command(name='nextofficial', description='Show details of the next official match')
    async def next_official(self, interaction: discord.Interaction):
        team = self._get_team(interaction)
        if not team:
            return await _no_team_response(interaction)

        calendar = team.get_calendar()
        events = calendar.get_upcoming_events(days=14)
        if not events:
            return await interaction.response.send_message("📅 No events scheduled!")

        officials = [e for e in events if _is_type(calendar.get_event_type(e), 'official')]
        if not officials:
            return await interaction.response.send_message("📅 No official matches scheduled!")

        officials.sort(key=lambda x: x['start_dt'])
        event = officials[0]
        event_type = calendar.get_event_type(event)
        roster = self.roster_storage.get_roster(_roster_key(event)) or None

        await interaction.response.send_message(
            embed=format_event_embed(event, roster=roster, event_type=event_type)
        )

    @app_commands.command(name='scrim', description='Show details of a specific event by ID')
    @app_commands.describe(event_id='The event ID from the calendar')
    async def scrim_details(self, interaction: discord.Interaction, event_id: str):
        team = self._get_team(interaction)
        if not team:
            return await _no_team_response(interaction)

        calendar = team.get_calendar()
        event = calendar.get_event(event_id)
        if not event:
            return await interaction.response.send_message(f"❌ Could not find event with ID: {event_id}")

        event_type = calendar.get_event_type(event)
        roster = self.roster_storage.get_roster(_roster_key(event)) or None

        await interaction.response.send_message(
            embed=format_event_embed(event, roster=roster, event_type=event_type)
        )

    @app_commands.command(name='today', description='Show events scheduled for today')
    async def today_scrims(self, interaction: discord.Interaction):
        from datetime import datetime
        team = self._get_team(interaction)
        if not team:
            return await _no_team_response(interaction)

        calendar = team.get_calendar()
        today = datetime.now().strftime('%Y-%m-%d')
        events = calendar.get_events(start_date=today, end_date=today)
        if not events:
            return await interaction.response.send_message("📅 No events scheduled for today!")

        event_types, rosters = self._enrich_events(events, calendar)
        embed = format_upcoming_events_embed(events, event_types, rosters)
        embed.title = "📋 Today's Events"
        embed.description = f"{len(events)} event{'s' if len(events) > 1 else ''} scheduled"
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='week', description='Show scrims scheduled for this week')
    async def week_scrims(self, interaction: discord.Interaction):
        team = self._get_team(interaction)
        if not team:
            return await _no_team_response(interaction)

        calendar = team.get_calendar()
        events = calendar.get_upcoming_events(days=7)
        if not events:
            return await interaction.response.send_message("📅 No scrims scheduled this week!")

        event_types, rosters = self._enrich_events(events, calendar)
        await interaction.response.send_message(
            embed=format_week_events_embed(events, event_types, rosters)
        )


def _roster_key(event: dict) -> str:
    """Return the team name to use for roster lookup."""
    return event.get('team_name') or event.get('title', '')


def _is_type(event_type: str, keyword: str) -> bool:
    return bool(event_type and keyword in event_type.lower())


async def setup(bot):
    await bot.add_cog(CalendarCommands(bot))
