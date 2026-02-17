import os


class Config:
    """Bot configuration singleton"""
    
    # TeamUp Calendar Configuration
    TEAMUP_API_KEY = os.getenv('TEAMUP_API_KEY')
    TEAMUP_CALENDAR_ID = os.getenv('TEAMUP_CALENDAR_ID')
    
    # Discord Configuration
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    REMINDER_CHANNEL_ID = int(os.getenv('REMINDER_CHANNEL_ID', 0))
    PLAYER_ROLE_ID = int(os.getenv('PLAYER_ROLE_ID', 0))
    COACH_ROLE_ID = int(os.getenv('COACH_ROLE_ID', 0))
    MANAGEMENT_ROLE_ID = int(os.getenv('MANAGEMENT_ROLE_ID', 0))
    
    # Reminder times (in hours before event)
    REMINDER_TIMES = [0.5]  # 30min before only
    
    # Check interval in minutes
    CHECK_INTERVAL = 5
    
    @classmethod
    def update_reminder_channel(cls, channel_id):
        """Update reminder channel ID"""
        cls.REMINDER_CHANNEL_ID = channel_id
        update_env_file('REMINDER_CHANNEL_ID', str(channel_id))
    
    @classmethod
    def is_configured(cls):
        """Check if bot is fully configured"""
        return all([
            cls.TEAMUP_API_KEY,
            cls.TEAMUP_CALENDAR_ID,
            cls.DISCORD_BOT_TOKEN,
            cls.REMINDER_CHANNEL_ID,
        ])


def update_env_file(key, value):
    """Update a value in the .env file"""
    env_path = '.env'
    
    try:
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        found = False
        with open(env_path, 'w') as f:
            for line in lines:
                if line.startswith(f'{key}='):
                    f.write(f'{key}={value}\n')
                    found = True
                else:
                    f.write(line)
            if not found:
                f.write(f'\n{key}={value}\n')
        
        return True
    except Exception as e:
        print(f"Error updating .env file: {e}")
        return False
