import os


class Config:
    """Shared bot-level configuration (not team-specific)."""

    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

    # Reminder times (in hours before event)
    REMINDER_TIMES = [0.5]  # 30 min before only

    # How often to check for upcoming reminders (minutes)
    CHECK_INTERVAL = 5
