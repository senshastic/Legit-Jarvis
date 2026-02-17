import discord
from discord.ext import commands
from discord import app_commands
from utils import TeamUpAPI, format_event_embed, format_bot_info_embed, Config


class AdminCommands(commands.Cog):
    """Administrative commands for bot configuration"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='setreminderchannel', description='Set current channel as reminder channel (Admin only)')
    @app_commands.default_permissions(administrator=True)
    async def set_reminder_channel(self, interaction: discord.Interaction):
        """Set current channel as reminder channel (Admin only)"""
        Config.update_reminder_channel(interaction.channel.id)
        await interaction.response.send_message(f"✅ Reminder channel set to {interaction.channel.mention}")

    @app_commands.command(name='testreminder', description='Send a test reminder to check if everything works (Admin only)')
    @app_commands.default_permissions(administrator=True)
    async def test_reminder(self, interaction: discord.Interaction):
        """Send a test reminder to check if everything works (Admin only)"""
        teamup = TeamUpAPI()
        events = teamup.get_upcoming_events(days=7)

        if not events:
            await interaction.response.send_message("❌ No events found to test with!")
            return

        # Use first event as test
        test_event = events[0]
        embed = format_event_embed(test_event)

        # Create mention string
        mentions = []
        if Config.PLAYER_ROLE_ID:
            mentions.append(f"<@&{Config.PLAYER_ROLE_ID}>")
        if Config.COACH_ROLE_ID:
            mentions.append(f"<@&{Config.COACH_ROLE_ID}>")

        mention_text = " ".join(mentions) if mentions else ""

        await interaction.response.send_message(content=f"🧪 **TEST REMINDER**\n{mention_text}", embed=embed)

    @app_commands.command(name='botinfo', description='Show bot configuration and status')
    async def show_bot_info(self, interaction: discord.Interaction):
        """Show bot configuration and status"""
        config = {
            'calendar_connected': Config.TEAMUP_API_KEY and Config.TEAMUP_CALENDAR_ID,
            'reminder_channel_id': Config.REMINDER_CHANNEL_ID,
            'check_interval': f"Every {Config.CHECK_INTERVAL} minutes",
            'reminder_times': ", ".join([f"{h}h" for h in Config.REMINDER_TIMES]),
            'player_role_id': Config.PLAYER_ROLE_ID,
            'coach_role_id': Config.COACH_ROLE_ID,
        }

        embed = format_bot_info_embed(config)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='ping', description='Check bot latency')
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: {latency}ms")

    @app_commands.command(name='reload', description='Reload a specific cog (Admin only)')
    @app_commands.describe(cog_name='Name of the cog to reload')
    @app_commands.default_permissions(administrator=True)
    async def reload_cog(self, interaction: discord.Interaction, cog_name: str):
        """Reload a specific cog (Admin only)"""
        try:
            await self.bot.reload_extension(cog_name)
            await interaction.response.send_message(f"✅ Reloaded cog: {cog_name}")
        except Exception as e:
            await interaction.response.send_message(f"❌ Error reloading cog: {e}")

    @app_commands.command(name='reloadall', description='Reload all cogs (Admin only)')
    @app_commands.default_permissions(administrator=True)
    async def reload_all_cogs(self, interaction: discord.Interaction):
        """Reload all cogs (Admin only)"""
        cogs = ['reminders', 'calendar_commands', 'admin_commands', 'help_commands', 'roster_commands']
        reloaded = []
        failed = []

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
