"""
Roster management commands for Discord bot.
Rosters are shared globally (all teams can see all rosters), but only
users with the coach role *for their own server* can create/delete them.
"""
import discord
from discord.ext import commands
from discord import app_commands
from roster_storage import RosterStorage
from typing import Literal


class RosterModal(discord.ui.Modal, title='Create Team Roster'):
    """Modal for creating/editing team rosters."""

    def __init__(self, team_name: str, existing_roster=None):
        super().__init__()
        self.team_name = team_name

        default_value = "\n".join(existing_roster) if existing_roster else ""

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
        players_text = self.players_input.value.strip()
        players = [p.strip() for p in players_text.split('\n') if p.strip()]

        if not players:
            return await interaction.response.send_message(
                "❌ You must add at least one player!", ephemeral=True
            )

        storage = RosterStorage()
        storage.set_roster(self.team_name, players)

        embed = discord.Embed(
            title=f"✅ Roster Saved for {self.team_name}",
            color=discord.Color.green()
        )
        embed.add_field(
            name=f"Players ({len(players)})",
            value="\n".join(f"{i+1}. {p}" for i, p in enumerate(players)),
            inline=False
        )
        embed.set_footer(text=f"Use /roster view {self.team_name} to view this roster anytime")
        await interaction.response.send_message(embed=embed)


class RosterCommands(commands.Cog):
    """Commands for managing team rosters."""

    def __init__(self, bot):
        self.bot = bot
        self.storage = RosterStorage()

    def _is_coach(self, interaction: discord.Interaction) -> bool:
        """Check if the user has the coach role for this guild."""
        team = self.bot.team_manager.get_team_for_guild(interaction.guild_id)
        if not team or not team.coach_role_id:
            # Fall back to administrator permission if no team/coach role configured
            return interaction.user.guild_permissions.administrator

        coach_role = discord.utils.get(interaction.guild.roles, id=team.coach_role_id)
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
        if action in ['create', 'delete'] and not self._is_coach(interaction):
            return await interaction.response.send_message(
                "❌ You must have the Coach role to manage rosters.", ephemeral=True
            )

        if action == 'list':
            await self._list_teams(interaction)
        elif action == 'view':
            if not team:
                return await interaction.response.send_message(
                    "❌ Please specify a team name.", ephemeral=True
                )
            await self._view_roster(interaction, team)
        elif action == 'create':
            if not team:
                return await interaction.response.send_message(
                    "❌ Please specify a team name.", ephemeral=True
                )
            await self._create_roster(interaction, team)
        elif action == 'delete':
            if not team:
                return await interaction.response.send_message(
                    "❌ Please specify a team name.", ephemeral=True
                )
            await self._delete_roster(interaction, team)

    async def _create_roster(self, interaction: discord.Interaction, team_name: str):
        existing_roster = self.storage.get_roster(team_name)
        modal = RosterModal(team_name, existing_roster)
        await interaction.response.send_modal(modal)

    async def _view_roster(self, interaction: discord.Interaction, team_name: str):
        roster = self.storage.get_roster(team_name)
        if not roster:
            return await interaction.response.send_message(
                f"❌ No roster found for team **{team_name}**.", ephemeral=True
            )

        embed = discord.Embed(
            title=f"📋 Roster for {team_name}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name=f"Players ({len(roster)})",
            value="\n".join(f"{i+1}. {p}" for i, p in enumerate(roster)),
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    async def _delete_roster(self, interaction: discord.Interaction, team_name: str):
        if self.storage.delete_roster(team_name):
            await interaction.response.send_message(f"✅ Roster for **{team_name}** has been deleted.")
        else:
            await interaction.response.send_message(
                f"❌ No roster found for team **{team_name}**.", ephemeral=True
            )

    async def _list_teams(self, interaction: discord.Interaction):
        teams = self.storage.list_all_teams()
        if not teams:
            return await interaction.response.send_message(
                "📋 No teams have rosters yet.", ephemeral=True
            )

        embed = discord.Embed(
            title="📋 All Teams with Rosters",
            description="\n".join(f"• {t}" for t in teams),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Total: {len(teams)} team(s)")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(RosterCommands(bot))
