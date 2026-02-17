import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal


class HelpCommands(commands.Cog):
    """Help and information commands"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='help', description='Show available commands')
    @app_commands.describe(category='Choose which help category to view')
    async def help_command(
        self,
        interaction: discord.Interaction,
        category: Literal['general', 'admin'] = 'general'
    ):
        """Show available commands"""
        if category == 'admin':
            await self.show_admin_help(interaction)
        else:
            await self.show_general_help(interaction)

    async def show_general_help(self, interaction: discord.Interaction):
        """Show general user commands"""
        embed = discord.Embed(
            title="📖 Marvel Rivals Scrim Bot - Commands",
            color=discord.Color.purple(),
            description="Commands for viewing and managing scrim schedules"
        )

        # Calendar Commands
        embed.add_field(
            name="📅 Calendar Commands",
            value=(
                "`/upcoming` - List all upcoming scrims\n"
                "`/nextscrim` - Show next scheduled scrim\n"
                "`/today` - Show today's scrims\n"
                "`/week` - Show this week's scrims\n"
                "`/scrim <event_id>` - Show specific scrim details"
            ),
            inline=False
        )

        # Roster Commands
        embed.add_field(
            name="👥 Roster Commands",
            value=(
                "`/roster create <team>` - Create roster for a team\n"
                "`/roster view <team>` - View team roster\n"
                "`/roster list` - List all teams\n"
                "`/roster delete <team>` - Delete a roster"
            ),
            inline=False
        )

        # Info Commands
        embed.add_field(
            name="ℹ️ Information",
            value=(
                "`/botinfo` - Show bot configuration\n"
                "`/ping` - Check bot latency\n"
                "`/help admin` - Show admin commands"
            ),
            inline=False
        )

        embed.set_footer(text="Bot automatically sends reminders 24h, 2h, and 30min before scrims")

        await interaction.response.send_message(embed=embed)

    async def show_admin_help(self, interaction: discord.Interaction):
        """Show admin-only commands"""
        embed = discord.Embed(
            title="🔧 Admin Commands",
            color=discord.Color.orange(),
            description="Administrator-only commands"
        )

        embed.add_field(
            name="Configuration",
            value=(
                "`/setreminderchannel` - Set current channel for reminders\n"
                "`/testreminder` - Send a test reminder\n"
                "` !forcecheckremind` - Manually trigger reminder check (prefix only)"
            ),
            inline=False
        )

        embed.add_field(
            name="Maintenance",
            value=(
                "`/reload <cog_name>` - Reload specific cog\n"
                "`/reloadall` - Reload all cogs"
            ),
            inline=False
        )

        embed.set_footer(text="⚠️ These commands require Administrator permission")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='about', description='Show information about the bot')
    async def about(self, interaction: discord.Interaction):
        """Show information about the bot"""
        embed = discord.Embed(
            title="🎮 Marvel Rivals Scrim Bot",
            color=discord.Color.blue(),
            description="A Discord bot for managing Marvel Rivals team scrims and reminders"
        )

        embed.add_field(
            name="Features",
            value=(
                "• Automatic scrim reminders\n"
                "• TeamUp calendar integration\n"
                "• Role mentions for players and coaches\n"
                "• Easy event viewing and management\n"
                "• Team roster management"
            ),
            inline=False
        )

        embed.add_field(
            name="Calendar",
            value="Events are managed via TeamUp Calendar",
            inline=True
        )

        embed.add_field(
            name="Reminders",
            value="24h, 2h, and 30min before events",
            inline=True
        )

        embed.add_field(
            name="Support",
            value="Use `/help` to see all commands",
            inline=False
        )

        embed.set_footer(text=f"Bot serving {len(self.bot.guilds)} server{'s' if len(self.bot.guilds) > 1 else ''}")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCommands(bot))
