# Legit Jarvis - Marvel Rivals Scrim Management Bot

A Discord bot for managing Marvel Rivals esports team scrims, integrating with TeamUp Calendar to provide automated reminders, roster management, and team coordination features.

## Features

### 📅 Calendar Integration
- **TeamUp Calendar sync** - Automatically pulls events from your TeamUp calendar
- **Multiple event types** - Supports Scrims, Official Matches, VOD Reviews, and Warmups
- **Timezone support** - All times displayed in each user's local timezone using Discord timestamps

### 🔔 Automated Reminders
- **30-minute warnings** - Automatic reminders 30 minutes before events
- **Daily noon summary** - Daily message with today's schedule and motivational Marvel Rivals quotes
- **Smart notifications** - Pings relevant roles (Players, Coaches, Management)

### 👥 Roster Management
- **Team rosters** - Create and manage rosters for different teams
- **Auto-display** - Rosters automatically shown with matching calendar events
- **Easy management** - Coach-only commands for creating, editing, and deleting rosters

### 📊 Availability Tracking
- **Player reporting** - Players can report if they'll be late or missing for events
- **Event selection** - Autocomplete dropdown showing all upcoming events with dates
- **Additional notes** - Optional field for players to provide more context
- **Instant notifications** - Automatically notifies coaches and management

### 🎮 Marvel Rivals Theme
- **100+ inspirational quotes** - Character-themed motivational messages from Spider-Man, Iron Man, Thor, and more
- **Game mechanics references** - Quotes about team-ups, ultimates, positioning, and strategy
- **Daily motivation** - Random quote included in daily noon reminder

## Commands

### Calendar Commands
- `/next` - Show the next scheduled event (any type)
- `/nextscrim` - Show the next scrim specifically
- `/nextofficial` - Show the next official match
- `/today` - Show all events scheduled for today
- `/week` - Show all events for the upcoming week
- `/upcoming` - List upcoming events for the next 7 days
- `/scrim <event_id>` - Show details of a specific event by ID

### Roster Commands
- `/roster create <team>` - Create or edit a team roster (Coach only)
- `/roster view <team>` - View a team's roster
- `/roster delete <team>` - Delete a team roster (Coach only)
- `/roster list` - List all teams with rosters

### Availability Commands
- `/availability` - Report if you'll be late or missing an event
  - Select event from autocomplete dropdown
  - Choose status: Late or Missing
  - Add optional notes for context

### Admin Commands
- `/setreminderchannel` - Set the current channel as the reminder channel (Admin only)
- `/testreminder` - Send a test reminder to verify setup (Admin only)
- `/botinfo` - Show bot configuration and status
- `/ping` - Check bot latency
- `/reload <cog>` - Reload a specific cog (Admin only)
- `/reloadall` - Reload all cogs (Admin only)
- `/help` - Show all available commands
- `/about` - Show information about the bot

### Owner-Only Commands
- `!sync` - Sync slash commands with Discord (updates command list)
- `!forcecheckremind` - Manually trigger reminder check
- `!forcedaily` - Manually trigger daily noon reminder

## Setup

### Prerequisites
- Python 3.9+
- Discord Bot Token
- TeamUp Calendar API Key and Calendar ID

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/LegitJarvis.git
   cd LegitJarvis
   ```

2. **Install dependencies**
   ```bash
   pip install discord.py python-dotenv requests
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Discord Bot Configuration
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   
   # TeamUp Calendar Configuration
   TEAMUP_API_KEY=your_teamup_api_key_here
   TEAMUP_CALENDAR_ID=your_calendar_id_here
   
   # Discord Channel & Role IDs
   REMINDER_CHANNEL_ID=your_reminder_channel_id
   PLAYER_ROLE_ID=your_player_role_id
   COACH_ROLE_ID=your_coach_role_id
   MANAGEMENT_ROLE_ID=your_management_role_id
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

5. **Sync commands**
   
   In Discord, use the `!sync` command to register all slash commands.

### Getting Your Credentials

#### Discord Bot Token
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token
5. Enable these Privileged Gateway Intents:
   - Message Content Intent
   - Server Members Intent (optional)

#### TeamUp API Key
1. Log in to [TeamUp Calendar](https://teamup.com/)
2. Go to Settings → Add-ons → API
3. Create a new API key with read access
4. Copy the API key and Calendar ID

#### Discord IDs
- Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
- Right-click channels/roles to copy their IDs

## Project Structure

```
LegitJarvis/
├── bot.py                      # Main bot file
├── config.py                   # Configuration management
├── utils.py                    # Utility functions and TeamUp API
├── embeds.py                   # Discord embed formatters
├── roster_storage.py           # Roster data management
├── reminders.py                # Reminder system cog
├── calendar_commands.py        # Calendar command cog
├── availability_commands.py    # Availability reporting cog
├── roster_commands.py          # Roster management cog
├── admin_commands.py           # Admin command cog
├── help_commands.py            # Help command cog
├── .env                        # Environment variables (not in repo)
├── .gitignore                  # Git ignore file
└── README.md                   # This file
```

## Features in Detail

### Automated Reminder System
The bot checks for upcoming events every 5 minutes and sends reminders:
- **30 minutes before** each event
- Mentions player and coach roles
- Shows event details, roster, and event type
- Prevents duplicate reminders

### Daily Noon Reminder
Every day at 12:00 PM, the bot sends:
- A random Marvel Rivals inspirational quote
- Today's complete schedule
- Event types with emojis (🎮 Scrim, 🏆 Official, 🎥 VOD, 🔥 Warmup)
- Full rosters for each event
- Motivational footer message

### Roster Integration
When viewing events, the bot automatically:
- Looks up the roster based on the event title (team name)
- Displays the full roster in the event embed
- Shows player count and all player names
- Works across all calendar commands

### Smart Event Filtering
- `/nextscrim` only shows events from "Scrim" subcalendars
- `/nextofficial` only shows events from "Official" subcalendars
- Filtering is case-insensitive and flexible

## Configuration

### Reminder Times
Edit `config.py` to change reminder intervals:
```python
REMINDER_TIMES = [0.5]  # Hours before event (0.5 = 30 minutes)
```

### Check Interval
Change how often the bot checks for reminders:
```python
CHECK_INTERVAL = 5  # Minutes
```

### Daily Reminder Time
Modify the daily reminder time in `reminders.py`:
```python
@tasks.loop(time=time(hour=12, minute=0))  # 12:00 PM
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Calendar integration powered by [TeamUp](https://www.teamup.com/)
- Inspired by Marvel Rivals and competitive esports team management needs

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Note**: This bot is designed for Marvel Rivals esports team management. Make sure to never share your `.env` file or expose your API keys and bot tokens.
