"""
Player availability reporting commands.
Allows players to report when they'll be late or missing events.
"""
import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
from datetime import datetime
from utils import TeamUpAPI, Config


class AvailabilityCommands(commands.Cog):
    """Commands for players to report availability issues."""

    def __init__(self, bot):
        self.bot = bot
        self._event_cache = []
        self._cache_time = None

    async def event_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for event selection showing title and date/time"""
        # Refresh cache if needed (cache for 5 minutes)
        from datetime import datetime, timedelta
        now = datetime.now()
        if not self._cache_time or (now - self._cache_time).total_seconds() > 300:
            teamup = TeamUpAPI()
            self._event_cache = teamup.get_upcoming_events(days=14)
            self._cache_time = now

        if not self._event_cache:
            return []

        # Create choices with event title + date/time
        choices = []
        for event in self._event_cache[:25]:  # Discord limits to 25 choices
            start_time = datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))
            # Format: "Event Title - Feb 17, 3:00 PM"
            display_name = f"{event.get('title', 'Unknown')} - {start_time.strftime('%b %d, %I:%M %p')}"
            # Store event ID as the value
            choices.append(app_commands.Choice(name=display_name[:100], value=event['id']))

        # Filter based on current input
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
        """Report availability status for an event"""

        # Get the event by ID
        teamup = TeamUpAPI()
        events = teamup.get_upcoming_events(days=14)

        if not events:
            await interaction.response.send_message(
                "❌ No upcoming events found!",
                ephemeral=True
            )
            return

        # Find event by ID
        matching_event = None
        for e in events:
            if e['id'] == event:
                matching_event = e
                break

        if not matching_event:
            await interaction.response.send_message(
                "❌ Could not find the selected event!",
                ephemeral=True
            )
            return

        # Send notification to channel
        if not Config.REMINDER_CHANNEL_ID:
            await interaction.response.send_message(
                "❌ Reminder channel not configured!",
                ephemeral=True
            )
            return

        channel = self.bot.get_channel(Config.REMINDER_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message(
                "❌ Could not find reminder channel!",
                ephemeral=True
            )
            return

        # Create notification embed
        start_time = datetime.fromisoformat(matching_event['start_dt'].replace('Z', '+00:00'))
        unix_timestamp = int(start_time.timestamp())

        color = discord.Color.orange() if status == 'Late' else discord.Color.red()
        emoji = "⏰" if status == 'Late' else "❌"

        embed = discord.Embed(
            title=f"{emoji} Player Availability Update",
            color=color,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="Player",
            value=f"{interaction.user.mention}",
            inline=True
        )

        embed.add_field(
            name="Status",
            value=f"**{status}**",
            inline=True
        )

        embed.add_field(
            name="Event",
            value=f"{matching_event.get('title', 'Unknown')}\n<t:{unix_timestamp}:F>",
            inline=False
        )

        if notes:
            embed.add_field(
                name="Additional Information",
                value=notes,
                inline=False
            )

        embed.set_footer(text=f"Reported by {interaction.user.display_name}")

        # Create mention string for coaches and management
        mentions = []
        if Config.COACH_ROLE_ID:
            mentions.append(f"<@&{Config.COACH_ROLE_ID}>")
        if Config.MANAGEMENT_ROLE_ID:
            mentions.append(f"<@&{Config.MANAGEMENT_ROLE_ID}>")

        mention_text = " ".join(mentions) if mentions else ""

        try:
            await channel.send(content=mention_text, embed=embed)
            await interaction.response.send_message(
                f"✅ Availability reported! Coaches and management have been notified that you'll be **{status.lower()}** for {matching_event.get('title', 'the event')}.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error sending notification: {e}",
                ephemeral=True
            )


async def setup(bot):
    """Setup function to add this cog to the bot."""
    await bot.add_cog(AvailabilityCommands(bot))
