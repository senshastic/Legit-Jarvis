"""
Player availability reporting commands.
Allows players to report when they'll be late or missing events.
Availability is fully isolated per guild — team A never sees team B's reports.
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
from datetime import datetime, timedelta


class AvailabilityCommands(commands.Cog):
    """Commands for players to report availability issues."""

    def __init__(self, bot):
        self.bot = bot
        # Per-guild event cache: {guild_id: (events_list, cache_timestamp)}
        self._event_cache: dict[int, tuple[list, datetime]] = {}

    def _get_team(self, interaction: discord.Interaction):
        return self.bot.team_manager.get_team_for_guild(interaction.guild_id)

    async def _get_cached_events(self, guild_id: int, team) -> list:
        """Return cached events for this guild, refreshing if older than 5 min."""
        cached = self._event_cache.get(guild_id)
        if cached:
            events, ts = cached
            if (datetime.now() - ts).total_seconds() <= 300:
                return events

        calendar = team.get_calendar()
        events = calendar.get_upcoming_events(days=14)
        self._event_cache[guild_id] = (events, datetime.now())
        return events

    async def event_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        team = self._get_team(interaction)
        if not team:
            return []

        events = await self._get_cached_events(interaction.guild_id, team)
        if not events:
            return []

        choices = []
        for event in events[:25]:
            start_time = datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))
            display = f"{event.get('title', 'Unknown')} - {start_time.strftime('%b %d, %I:%M %p')}"
            choices.append(app_commands.Choice(name=display[:100], value=event['id']))

        if current:
            choices = [c for c in choices if current.lower() in c.name.lower()]

        return choices[:25]

    @app_commands.command(name='availability', description='Report if you\'ll be late or missing an event')
    @app_commands.describe(
        status='Are you going to be late or missing?',
        event='Select the event from the list',
        notes='Additional information (optional)'
    )
    @app_commands.autocomplete(event=event_autocomplete)
    async def report_availability(
        self,
        interaction: discord.Interaction,
        status: Literal['Late', 'Missing'],
        event: str,
        notes: str = None
    ):
        team = self._get_team(interaction)
        if not team:
            return await interaction.response.send_message(
                "❌ This server is not configured. Add it to `teams.json`.",
                ephemeral=True
            )

        events = await self._get_cached_events(interaction.guild_id, team)
        if not events:
            return await interaction.response.send_message(
                "❌ No upcoming events found!", ephemeral=True
            )

        matching_event = next((e for e in events if e['id'] == event), None)
        if not matching_event:
            return await interaction.response.send_message(
                "❌ Could not find the selected event!", ephemeral=True
            )

        channel = self.bot.get_channel(team.reminder_channel_id)
        if not channel:
            return await interaction.response.send_message(
                "❌ Reminder channel not configured or not found!", ephemeral=True
            )

        start_time = datetime.fromisoformat(matching_event['start_dt'].replace('Z', '+00:00'))
        unix_timestamp = int(start_time.timestamp())

        color = discord.Color.orange() if status == 'Late' else discord.Color.red()
        emoji = "⏰" if status == 'Late' else "❌"

        embed = discord.Embed(
            title=f"{emoji} Player Availability Update",
            color=color,
            timestamp=datetime.now()
        )
        embed.add_field(name="Player", value=interaction.user.mention, inline=True)
        embed.add_field(name="Status", value=f"**{status}**", inline=True)
        embed.add_field(
            name="Event",
            value=f"{matching_event.get('title', 'Unknown')}\n<t:{unix_timestamp}:F>",
            inline=False
        )
        if notes:
            embed.add_field(name="Additional Information", value=notes, inline=False)
        embed.set_footer(text=f"Reported by {interaction.user.display_name}")

        mentions = []
        if team.coach_role_id:
            mentions.append(f"<@&{team.coach_role_id}>")
        if team.management_role_id:
            mentions.append(f"<@&{team.management_role_id}>")
        mention_text = " ".join(mentions)

        try:
            await channel.send(content=mention_text, embed=embed)

            # Push availability note to the calendar event
            calendar = team.get_calendar()
            emoji = "⏰" if status == 'Late' else "❌"
            cal_note = f"{emoji} {interaction.user.display_name} — {status}"
            if notes:
                cal_note += f": {notes}"
            calendar.append_availability_note(matching_event['id'], cal_note)

            await interaction.response.send_message(
                f"✅ Availability reported! Coaches and management have been notified that you'll be "
                f"**{status.lower()}** for {matching_event.get('title', 'the event')}.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error sending notification: {e}", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(AvailabilityCommands(bot))
