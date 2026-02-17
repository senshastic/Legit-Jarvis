import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store bot start time
bot.start_time = None


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    print('Loading cogs...')

    # Load all cogs
    await load_cogs()

    print('Bot is ready!')
    print('💡 Use /sync to register slash commands with Discord')


async def load_cogs():
    """Load all cog files"""
    cogs = [
        'reminders',
        'calendar_commands',
        'admin_commands',
        'help_commands',
        'roster_commands',
        'availability_commands'
    ]

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'✅ Loaded {cog}')
        except Exception as e:
            print(f'❌ Failed to load {cog}: {e}')


@bot.command(name='sync')
@commands.is_owner()
async def sync(ctx):
    """Sync slash commands with Discord (Owner only)"""
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ Synced {len(synced)} slash command(s)!")
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        await ctx.send(f"❌ Failed to sync commands: {e}")
        print(f"Sync error: {e}")


@bot.event
async def on_command_error(ctx, error):
    """Global error handler"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    elif isinstance(error, commands.NotOwner):
        await ctx.send("❌ Only the bot owner can use this command!")
    else:
        print(f'Error: {error}')
        await ctx.send(f"❌ An error occurred: {str(error)}")


if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables")
        exit(1)
    
    bot.run(TOKEN)
