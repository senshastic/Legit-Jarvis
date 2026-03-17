# Legit Jarvis — Marvel Rivals Team Management Bot

A Discord bot built for competitive Marvel Rivals teams, used by partner teams in the Marvel Rivals Ignite ecosystem. Handles calendar integration, automated reminders, roster management, and availability tracking — all configurable per team and per server.

## Features

### 📅 Calendar Integration
- **Multi-calendar support** — Connects to TeamUp or Google Calendar depending on the team
- **Multiple event types** — Scrims, Official Matches, VOD Reviews, and Warmups
- **Timezone support** — All times shown in each user's local timezone via Discord timestamps

### 🔔 Automated Reminders
- **30-minute warnings** — Automatic reminders before each event
- **Daily noon summary** — Today's schedule with rosters and motivational Marvel Rivals quotes
- **Smart notifications** — Pings the right roles (Players, Coaches, Management) per server

### 👥 Roster Management
- **Shared roster database** — Rosters are available across the bot's servers
- **Auto-display** — Rosters automatically pulled and shown alongside calendar events
- **Role-gated management** — Only users with the Coach role can create or edit rosters

### 📊 Availability Tracking
- **Per-server isolation** — Each team's availability reports stay in their own server
- **Event autocomplete** — Dropdown showing upcoming events with dates and times
- **Instant notifications** — Coaches and management are pinged automatically

### 🏢 Multi-Team Support
- **Multiple servers** — One bot instance runs across multiple Discord servers
- **Per-team config** — Each server has its own calendar, channels, and roles
- **Independent reminders** — Each team gets its own reminder channel and schedule

## Commands

### Calendar Commands
- `/next` — Show the next scheduled event
- `/nextscrim` — Show the next scrim
- `/nextofficial` — Show the next official match
- `/today` — Show all events scheduled for today
- `/week` — Show all events this week
- `/upcoming` — List upcoming events for the next 7 days
- `/scrim <event_id>` — Show details of a specific event by ID

### Roster Commands
- `/roster create <team>` — Create or edit a team roster (Coach only)
- `/roster view <team>` — View a team's roster
- `/roster delete <team>` — Delete a team roster (Coach only)
- `/roster list` — List all teams with rosters

### Availability Commands
- `/availability` — Report if you'll be late or missing an event
  - Select event from autocomplete dropdown
  - Choose status: Late or Missing
  - Add optional notes

### Admin Commands
- `/setreminderchannel` — Set the current channel as the reminder channel (Admin only)
- `/testreminder` — Send a test reminder (Admin only)
- `/botinfo` — Show this server's bot configuration and status
- `/ping` — Check bot latency
- `/reload <cog>` — Reload a specific cog (Admin only)
- `/reloadall` — Reload all cogs (Admin only)

### Owner-Only Commands
- `!sync` — Sync slash commands with Discord
- `!forcecheckremind` — Manually trigger a reminder check for this server
- `!forcedaily` — Manually trigger the daily noon summary for this server

## Setup

### Prerequisites
- Python 3.9+
- Discord Bot Token
- TeamUp API Key (for TeamUp teams) and/or Google Cloud service account (for Google Calendar teams)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/LegitJarvis.git
   cd LegitJarvis
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure `.env`**
   ```env
   DISCORD_BOT_TOKEN=your_discord_bot_token

   # One entry per team — name matches the key in teams.json
   TEAM1_TEAMUP_API_KEY=your_teamup_api_key
   TEAM2_GOOGLE_CREDENTIALS_FILE=path/to/service-account.json
   ```

4. **Configure `teams.json`**
   ```json
   {
     "teams": [
       {
         "team_id": "team1",
         "name": "Team Name",
         "guild_id": 123456789,
         "calendar_type": "teamup",
         "reminder_channel_id": 123456789,
         "player_role_id": 123456789,
         "coach_role_id": 123456789,
         "management_role_id": 123456789,
         "teamup_calendar_id": "your_calendar_id",
         "teamup_api_key_env": "TEAM1_TEAMUP_API_KEY"
       },
       {
         "team_id": "team2",
         "name": "Team Name",
         "guild_id": 987654321,
         "calendar_type": "google",
         "reminder_channel_id": 987654321,
         "player_role_id": 987654321,
         "coach_role_id": 987654321,
         "management_role_id": 987654321,
         "google_calendar_id": "xxx@group.calendar.google.com",
         "google_credentials_file": "service-account.json"
       }
     ]
   }
   ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

6. **Sync commands** — In each Discord server, run `!sync` to register slash commands.

### Google Calendar Setup
1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable the **Google Calendar API**
3. Create a **Service Account** and download the JSON key file
4. Share your Google Calendar with the service account email address (read-only access is enough)
5. Place the JSON key file in the bot directory and reference it in `teams.json`

## Project Structure

```
LegitJarvis/
├── bot.py                    # Entry point
├── config.py                 # Shared bot settings
├── team_manager.py           # Multi-team config loader
├── calendar_provider.py      # Abstract calendar interface
├── teamup_api.py             # TeamUp calendar provider
├── google_calendar_api.py    # Google Calendar provider
├── roster_storage.py         # Roster persistence (rosters.json)
├── embeds.py                 # Discord embed formatters
├── reminders.py              # Automated reminder cog
├── calendar_commands.py      # Calendar slash commands cog
├── availability_commands.py  # Availability reporting cog
├── roster_commands.py        # Roster management cog
├── admin_commands.py         # Admin commands cog
├── help_commands.py          # Help commands cog
├── teams.json                # Team configuration
├── .env                      # Secrets (not in repo)
└── .gitignore
```

## Configuration

### Reminder timing
Edit `config.py`:
```python
REMINDER_TIMES = [0.5]  # Hours before event (0.5 = 30 min)
CHECK_INTERVAL = 5      # Minutes between checks
```

### Daily reminder time
Edit `reminders.py`:
```python
@tasks.loop(time=time(hour=12, minute=0))  # 12:00 PM
```

## Contributing

Contributions are not welcome, leave me alone.

## License

MIT License

## Acknowledgments

- Built with [discord.py](https://github.com/Rapptz/discord.py)
- TeamUp integration via [TeamUp Calendar API](https://www.teamup.com/)
- Google Calendar integration via [Google Calendar API](https://developers.google.com/calendar)
- Built for Marvel Rivals partner teams competing in the [Marvel Rivals Ignite](https://www.marvelrivalsesports.com/) ecosystem
