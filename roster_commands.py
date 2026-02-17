"""
Roster management commands for Discord bot.
Allows coaches to create and manage team rosters.
"""
import discord
from discord.ext import commands
from discord import app_commands
from config import Config
from roster_storage import RosterStorage
from typing import Literal


class RosterModal(discord.ui.Modal, title='Create Team Roster'):
    """Modal for creating/editing team rosters"""

    def __init__(self, team_name: str, existing_roster=None):
        super().__init__()
        self.team_name = team_name
        self.existing_roster = existing_roster

        # Pre-fill with existing roster if editing
        default_value = ""
        if existing_roster:
            default_value = "\n".join(existing_roster)

        self.players_input = discord.ui.TextInput(
            label='Player Names',
            style=discord.TextStyle.paragraph,
            placeholder='Enter player names, one per line...\nExample:\nPlayer1\nPlayer2\nPlayer3',
            required=True,
            max_length=1000,
            default=default_value
        )
        self.add_item(self.players_input)

    async def on_submit(self, interaction: discord.Interaction):
        """Handle roster submission"""
        # Parse player names from input
        players_text = self.players_input.value.strip()
        players = [p.strip() for p in players_text.split('\n') if p.strip()]

        if not players:
            await interaction.response.send_message("❌ You must add at least one player!", ephemeral=True)
            return

        # Save roster
        storage = RosterStorage()
        storage.set_roster(self.team_name, players)

        # Confirmation embed
        embed = discord.Embed(
            title=f"✅ Roster Saved for {self.team_name}",
            color=discord.Color.green()
        )
        embed.add_field(
            name=f"Players ({len(players)})",
            value="\n".join(f"{i+1}. {player}" for i, player in enumerate(players)),
            inline=False
        )
        embed.set_footer(text=f"Use /roster view {self.team_name} to view this roster anytime")

        await interaction.response.send_message(embed=embed)


class RosterCommands(commands.Cog):
    """Commands for managing team rosters."""

    def __init__(self, bot):
        """
        Initialize the RosterCommands cog.

        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.storage = RosterStorage()

    def _is_coach(self, interaction: discord.Interaction) -> bool:
        """
        Check if the user has the coach role.

        Args:
            interaction: Command interaction

        Returns:
            True if user has coach role, False otherwise
        """
        if not Config.COACH_ROLE_ID:
            return interaction.user.guild_permissions.administrator

        coach_role = discord.utils.get(interaction.guild.roles, id=int(Config.COACH_ROLE_ID))
        return coach_role in interaction.user.roles if coach_role else False

    @app_commands.command(name='roster', description='Manage team rosters (Coach only)')
    @app_commands.describe(
        action='Choose what to do with the roster',
        team='Name of the team'
    )
    async def roster(
        self,
        interaction: discord.Interaction,
        action: Literal['create', 'view', 'delete', 'list'],
        team: str = None
    ):
        """
        Manage team rosters.

        Actions:
            create - Create or edit a team roster
            view - View a team's roster
            delete - Delete a team's roster
            list - List all teams with rosters
        """
        # Check coach permission for create/delete
        if action in ['create', 'delete'] and not self._is_coach(interaction):
            await interaction.response.send_message("❌ You must have the Coach role to manage rosters.", ephemeral=True)
            return

        if action == 'list':
            await self._list_teams(interaction)
        elif action == 'view':
            if not team:
                await interaction.response.send_message("❌ Please specify a team name.", ephemeral=True)
                return
            await self._view_roster(interaction, team)
        elif action == 'create':
            if not team:
                await interaction.response.send_message("❌ Please specify a team name.", ephemeral=True)
                return
            await self._create_roster(interaction, team)
        elif action == 'delete':
            if not team:
                await interaction.response.send_message("❌ Please specify a team name.", ephemeral=True)
                return
            await self._delete_roster(interaction, team)

    async def _create_roster(self, interaction: discord.Interaction, team_name: str):
        """
        Open modal for roster creation/editing.

        Args:
            interaction: Command interaction
            team_name: Name of the team
        """
        # Check if roster already exists
        existing_roster = self.storage.get_roster(team_name)

        # Open modal with existing roster if editing
        modal = RosterModal(team_name, existing_roster)
        await interaction.response.send_modal(modal)

    async def _view_roster(self, interaction: discord.Interaction, team_name: str):
        """
        View a team's roster.

        Args:
            interaction: Command interaction
            team_name: Name of the team
        """
        roster = self.storage.get_roster(team_name)

        if not roster:
            await interaction.response.send_message(f"❌ No roster found for team **{team_name}**.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📋 Roster for {team_name}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name=f"Players ({len(roster)})",
            value="\n".join(f"{i+1}. {player}" for i, player in enumerate(roster)),
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    async def _delete_roster(self, interaction: discord.Interaction, team_name: str):
        """
        Delete a team's roster.

        Args:
            interaction: Command interaction
            team_name: Name of the team
        """
        if self.storage.delete_roster(team_name):
            await interaction.response.send_message(f"✅ Roster for **{team_name}** has been deleted.")
        else:
            await interaction.response.send_message(f"❌ No roster found for team **{team_name}**.", ephemeral=True)

    async def _list_teams(self, interaction: discord.Interaction):
        """
        List all teams with rosters.

        Args:
            interaction: Command interaction
        """
        teams = self.storage.list_all_teams()

        if not teams:
            await interaction.response.send_message("📋 No teams have rosters yet.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📋 All Teams with Rosters",
            description="\n".join(f"• {team}" for team in teams),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Total: {len(teams)} team(s)")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    """
    Setup function to add this cog to the bot.

    Args:
        bot: The Discord bot instance
    """
    await bot.add_cog(RosterCommands(bot))
