import discord
from discord.ext import commands
from discord import app_commands
from embeds import format_event_embed, format_bot_info_embed


class AdminCommands(commands.Cog):
    """Administrative commands for bot configuration."""

    def __init__(self, bot):
        self.bot = bot

    def _get_team(self, interaction: discord.Interaction):
        return self.bot.team_manager.get_team_for_guild(interaction.guild_id)

    @app_commands.command(name='setreminderchannel', description='Set current channel as reminder channel (Admin only)')
    @app_commands.default_permissions(administrator=True)
    async def set_reminder_channel(self, interaction: discord.Interaction):
        team = self._get_team(interaction)
        if not team:
            return await interaction.response.send_message(
                "❌ This server is not configured in `teams.json`.", ephemeral=True
            )
        self.bot.team_manager.update_reminder_channel(interaction.guild_id, interaction.channel.id)
        await interaction.response.send_message(
            f"✅ Reminder channel set to {interaction.channel.mention}"
        )

    @app_commands.command(name='testreminder', description='Send a test reminder (Admin only)')
    @app_commands.default_permissions(administrator=True)
    async def test_reminder(self, interaction: discord.Interaction):
        team = self._get_team(interaction)
        if not team:
            return await interaction.response.send_message(
                "❌ This server is not configured in `teams.json`.", ephemeral=True
            )

        calendar = team.get_calendar()
        events = calendar.get_upcoming_events(days=7)
        if not events:
            return await interaction.response.send_message("❌ No events found to test with!")

        event = events[0]
        event_type = calendar.get_event_type(event)
        embed = format_event_embed(event, event_type=event_type)

        mentions = []
        if team.player_role_id:
            mentions.append(f"<@&{team.player_role_id}>")
        if team.coach_role_id:
            mentions.append(f"<@&{team.coach_role_id}>")
        mention_text = " ".join(mentions)

        await interaction.response.send_message(
            content=f"🧪 **TEST REMINDER**\n{mention_text}", embed=embed
        )

    @app_commands.command(name='botinfo', description='Show bot configuration and status')
    async def show_bot_info(self, interaction: discord.Interaction):
        team = self._get_team(interaction)
        if not team:
            return await interaction.response.send_message(
                "❌ This server is not configured in `teams.json`.", ephemeral=True
            )

        from config import Config
        config = {
            'calendar_connected': team.is_configured(),
            'reminder_channel_id': team.reminder_channel_id,
            'check_interval': f"Every {Config.CHECK_INTERVAL} minutes",
            'reminder_times': ", ".join([f"{h}h" for h in Config.REMINDER_TIMES]),
            'player_role_id': team.player_role_id,
            'coach_role_id': team.coach_role_id,
            'team_name': team.name,
            'calendar_type': team.calendar_type,
        }
        embed = format_bot_info_embed(config)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='ping', description='Check bot latency')
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms")

    @app_commands.command(name='reload', description='Reload a specific cog (Admin only)')
    @app_commands.describe(cog_name='Name of the cog to reload')
    @app_commands.default_permissions(administrator=True)
    async def reload_cog(self, interaction: discord.Interaction, cog_name: str):
        try:
            await self.bot.reload_extension(cog_name)
            await interaction.response.send_message(f"✅ Reloaded cog: {cog_name}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Error reloading cog: {e}")

    @app_commands.command(name='reloadall', description='Reload all cogs (Admin only)')
    @app_commands.default_permissions(administrator=True)
    async def reload_all_cogs(self, interaction: discord.Interaction):
        cogs = ['reminders', 'calendar_commands', 'admin_commands', 'help_commands',
                'roster_commands', 'availability_commands']
        reloaded, failed = [], []
        for cog in cogs:
            try:
                await self.bot.reload_extension(cog)
                reloaded.append(cog)
            except Exception as e:
                failed.append(f"{cog}: {str(e)}")

        message = "**Reload Results:**\n"
        if reloaded:
            message += f"✅ Reloaded: {', '.join(reloaded)}\n"
        if failed:
            message += f"❌ Failed: {', '.join(failed)}"
        await interaction.response.send_message(message)


async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
