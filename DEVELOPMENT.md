# Development Guide

## Project Architecture

The bot uses a **cog-based architecture** for modularity and maintainability.

### File Organization

```
marvel_rivals_bot/
├── bot.py                    # Main entry point, loads cogs
├── cogs/                     # Feature modules
│   ├── reminders.py         # Background task for auto-reminders
│   ├── calendar_commands.py # User commands for viewing calendar
│   ├── admin_commands.py    # Admin-only configuration commands
│   └── help_commands.py     # Help system
└── utils/                    # Shared utilities
    ├── teamup_api.py        # TeamUp API wrapper
    ├── embeds.py            # Discord embed formatters
    └── config.py            # Configuration management
```

## Understanding Cogs

**What is a Cog?**
A cog is a collection of commands, listeners, and tasks grouped by functionality.

**Benefits:**
- ✅ Organize commands by feature
- ✅ Hot-reload without restarting bot
- ✅ Easy to enable/disable features
- ✅ Better code organization

### Cog Structure

```python
from discord.ext import commands

class MyCog(commands.Cog):
    """Description of what this cog does"""
    
    def __init__(self, bot):
        self.bot = bot
        # Initialize any state here
    
    @commands.command(name='mycommand')
    async def my_command(self, ctx):
        """Command help text"""
        await ctx.send("Response")
    
    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        pass

async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

## Adding New Features

### 1. Adding a New Command to Existing Cog

Edit the appropriate cog file:

```python
# cogs/calendar_commands.py
@commands.command(name='mynewcommand')
async def my_new_command(self, ctx):
    """Description"""
    await ctx.send("Hello!")
```

Reload the cog in Discord:
```
!reload calendar_commands
```

### 2. Creating a New Cog

**Step 1:** Create a new file in `cogs/`

```python
# cogs/my_feature.py
import discord
from discord.ext import commands
from utils import TeamUpAPI, Config

class MyFeature(commands.Cog):
    """Feature description"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='test')
    async def test_command(self, ctx):
        await ctx.send("Works!")

async def setup(bot):
    await bot.add_cog(MyFeature(bot))
```

**Step 2:** Add to bot.py

```python
# bot.py
cogs = [
    'cogs.reminders',
    'cogs.calendar_commands',
    'cogs.admin_commands',
    'cogs.help_commands',
    'cogs.my_feature'  # Add here
]
```

**Step 3:** Restart bot or use `!reloadall`

### 3. Adding Utility Functions

Add shared code to `utils/`:

```python
# utils/my_util.py
def my_helper_function():
    """Utility function"""
    return "result"
```

Import in `utils/__init__.py`:

```python
from .my_util import my_helper_function

__all__ = [..., 'my_helper_function']
```

Use in any cog:

```python
from utils import my_helper_function
```

## Common Tasks

### Adding a Background Task

```python
from discord.ext import tasks

class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.my_task.start()
    
    @tasks.loop(minutes=10)
    async def my_task(self):
        """Runs every 10 minutes"""
        print("Task running!")
    
    @my_task.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()
    
    def cog_unload(self):
        self.my_task.cancel()
```

### Adding Event Listeners

```python
@commands.Cog.listener()
async def on_message(self, message):
    """Triggered when any message is sent"""
    if message.author.bot:
        return
    # Do something
```

### Adding Permissions Check

```python
@commands.command()
@commands.has_permissions(administrator=True)
async def admin_only(self, ctx):
    """Only admins can use this"""
    await ctx.send("Admin command!")
```

### Adding Command Arguments

```python
@commands.command()
async def greet(self, ctx, member: discord.Member):
    """Greet a member: !greet @username"""
    await ctx.send(f"Hello {member.mention}!")

@commands.command()
async def say(self, ctx, *, message: str):
    """Say something: !say hello world"""
    await ctx.send(message)
```

## Best Practices

1. **Error Handling**
   ```python
   @commands.command()
   async def mycommand(self, ctx):
       try:
           # Your code
           pass
       except Exception as e:
           await ctx.send(f"❌ Error: {e}")
   ```

2. **Use Config for Settings**
   ```python
   from utils import Config
   
   if Config.PLAYER_ROLE_ID:
       # Use the configured role
   ```

3. **Consistent Embeds**
   ```python
   from utils import format_event_embed
   
   embed = format_event_embed(event)
   await ctx.send(embed=embed)
   ```

4. **Async/Await**
   - Always use `await` for async functions
   - Use `async def` for coroutines
   - Don't block the event loop

5. **Documentation**
   - Add docstrings to commands (shows in help)
   - Comment complex logic
   - Update README.md with new features

## Testing

1. **Test in Development Server**
   - Create a test Discord server
   - Test all new commands
   - Check permissions

2. **Use Test Commands**
   ```
   !testreminder  # Test reminder system
   !ping          # Check bot is responsive
   !botinfo       # Check configuration
   ```

3. **Check Logs**
   - Watch console output
   - Look for error messages
   - Verify tasks are running

## Troubleshooting

### Cog Won't Load
- Check syntax errors
- Ensure `async def setup(bot)` exists
- Verify imports are correct

### Command Not Working
- Check if cog is loaded: `!botinfo`
- Reload cog: `!reload <cogname>`
- Check bot has permissions

### Background Task Not Running
- Check `@tasks.loop()` decorator
- Ensure `.start()` is called in `__init__`
- Add `@task.before_loop` with `wait_until_ready()`

## Resources

- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs)
- [TeamUp API Docs](https://apidocs.teamup.com/)

## Contributing

1. Create a new branch for features
2. Test thoroughly
3. Update documentation
4. Use descriptive commit messages
