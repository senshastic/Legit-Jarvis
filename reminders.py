import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
from utils import TeamUpAPI, format_event_embed, Config
from roster_storage import RosterStorage
import random


# Marvel Rivals themed inspirational quotes
INSPIRATIONAL_QUOTES = [
    "With great power comes great responsibility. Let's web up this W! 🕷️",
    "I am Iron Man. And we're here to win. 🦾",
    "Assemble the team, secure the victory! 🛡️",
    "Even gods must prove themselves. Show them your power! ⚡",
    "The world needs heroes. Be one today! 🦸",
    "Hulk smash... the competition! 💚",
    "For Wakanda! For victory! 🐆",
    "I can do this all day. And we will! 🛡️",
    "It's clobberin' time! Let's dominate! 🪨",
    "Flame on! Heat up that performance! 🔥",
    "Welcome to die... said no winner ever. Let's prove them wrong! ⚔️",
    "Magneto never backs down. Neither do we! 🧲",
    "The Phoenix rises! Time to soar! 🔥",
    "Wolverine doesn't quit. We don't quit. 🦡",
    "Storm controls the battlefield. Control yours! ⛈️",
    "Spider-sense is tingling... it's telling me we're winning today! 🕸️",
    "Thor's hammer knows no defeat. Neither shall we! 🔨",
    "Black Panther strikes with precision. Execute the plan! 🐾",
    "Venom wants victory. Feed the hunger! 🖤",
    "Scarlet Witch bends reality. Bend the odds in our favor! ✨",
    "Doctor Strange sees all possibilities. We choose victory! 👁️",
    "Star-Lord's got the moves. Show them what you've got! 🎵",
    "Rocket's strategies never fail. Trust the process! 🦝",
    "Groot has one message: I am Groot! (We got this!) 🌳",
    "Punisher never misses. Neither should you! 💀",
    "Luna Snow brings the freeze! Ice them out! ❄️",
    "Hela's power is unstoppable. Channel that energy! 👑",
    "Loki's tricks win games. Outsmart them! 🐍",
    "Adam Warlock protects his team. Protect yours! ⭐",
    "Namor rules the depths. Rule this match! 🌊",
    "Together we stand, divided we fall. Stay united! 🤝",
    "Every ultimate tells a story. Make yours legendary! 💫",
    "Support your team like Mantis supports hers! 🦋",
    "Tank the damage, secure the point! 🛡️",
    "Flex DPS, flex on them! 💪",
    "Peni Parker brings the tech. Bring your A-game! 🤖",
    "Jeff the Shark knows no fear. Dive in! 🦈",
    "Squirrel Girl's optimism is unbeatable! Stay positive! 🐿️",
    "Cloak and Dagger work in perfect harmony. Sync up! 🌓",
    "Captain America leads by example. Lead your team! 🛡️",
    "The Punisher leaves no enemy standing. Finish strong! 💥",
    "Psylocke strikes from the shadows. Be unpredictable! 🗡️",
    "Moon Knight fights through the night. Never give up! 🌙",
    "Black Widow's precision is deadly. Aim for perfection! 🕷️",
    "Hawkeye never misses the shot that matters. Clutch it! 🏹",
    "Galacta hungers for victory. Stay hungry! 🌌",
    "Damage? I am the damage. 💢",
    "Strategist? More like victory architect! 🧠",
    "Vanguard leads the charge. Push forward! ⚔️",
    "Team up ability ready! Synergize and conquer! 🤜🤛",
    "Respawn and revenge! Come back stronger! ♻️",
    "Objective secured means victory secured! 🎯",
    "Map awareness wins games. Eyes open! 👀",
    "Ultimate economy is victory economy! 💎",
    "Positioning beats pure mechanics! 📍",
    "Cover your healer, secure your victory! 🏥",
    "Peel for your backline! Protect and win! 🛡️",
    "Communicate, coordinate, dominate! 📢",
    "One pick leads to one push! Create opportunities! 🎯",
    "Adapt or lose. We adapt! 🔄",
    "Counter-pick counter-play! Stay ahead! ♟️",
    "High ground is our ground! Take the advantage! ⬆️",
    "Flank watch saves lives! Stay aware! 👁️",
    "Focus fire, quick kill! Concentrate fire! 🔥",
    "Stagger punish wins fights! Capitalize! ⚡",
    "Spawn camp? More like spawn champ! 🏕️",
    "This isn't just a game, it's a legacy! 🏆",
    "The suit can take a hit. Can you? Toughen up! 🦾",
    "Tony Stark built this in a cave! What's your excuse? 🔧",
    "Strange things happen when we work together! 🌀",
    "I'm always angry. Channel that energy! 💪",
    "We are Venom. We are victorious! 🖤",
    "With Mjolnir in hand, victory is certain! ⚡",
    "Wakanda forever! Our team forever! 👊",
    "The Friendly Neighborhood team always wins! 🏘️",
    "Avengers! Let's make it count! 🦸‍♂️",
    "X-Men unite for the perfect team fight! ✖️",
    "Fantastic Four strategies for fantastic wins! 4️⃣",
    "Guardians protect what matters. Protect the objective! 🚀",
    "This is the way. To victory! 🎯",
    "Excelsior! Onward to greatness! 📈",
    "True believers never surrender! ✊",
    "Maximum effort for maximum results! 💯",
    "Healing factor kicks in! Bounce back! 🩹",
    "Bifrost to victory! Transport to the W! 🌈",
    "Mjolnir spinning = winning! Keep the momentum! 🔨",
    "Web them up! Control the fight! 🕸️",
    "Repulsor rays to victory! Blast through! 💥",
    "Adamantium will never breaks. Neither will we! 💎",
    "Vibranium strong! Unbreakable team! 🛡️",
    "Symbiote synergy wins games! 🖤",
    "Mutant and proud! Show that pride! ✖️",
    "Asgardian might! Godlike plays! ⚡",
    "Cosmic power flowing! Feel the energy! 🌌",
    "Mystic arts mastered! Control the match! 🔮",
    "Tech suit activated! Upgrade your gameplay! 🤖",
    "Spider-verse assembled! All hands on deck! 🕷️",
    "Infinity stones? We have infinity skills! 💎",
    "Snap! Half their team gone! Dominate! 🫰",
    "Assembled and ready to win! 🦸",
    "Heroes never die... they respawn and clutch! ⭐"
]


class Reminders(commands.Cog):
    """Automatic reminder system for scrims"""
    
    def __init__(self, bot):
        self.bot = bot
        self.sent_reminders = set()  # Track sent reminders to avoid duplicates
        self.roster_storage = RosterStorage()  # Initialize roster storage
        self.check_reminders.start()
        self.daily_noon_reminder.start()

    def cog_unload(self):
        """Cleanup when cog is unloaded"""
        self.check_reminders.cancel()
        self.daily_noon_reminder.cancel()
    
    @tasks.loop(minutes=Config.CHECK_INTERVAL)
    async def check_reminders(self):
        """Check for upcoming events and send reminders"""
        if not Config.REMINDER_CHANNEL_ID:
            return
        
        channel = self.bot.get_channel(Config.REMINDER_CHANNEL_ID)
        if not channel:
            print(f"Could not find channel with ID {Config.REMINDER_CHANNEL_ID}")
            return
        
        # Initialize TeamUp API
        teamup = TeamUpAPI()
        
        # Get events for next 7 days
        events = teamup.get_upcoming_events(days=7)
        
        for event in events:
            for hours in Config.REMINDER_TIMES:
                if self.should_send_reminder(event, hours):
                    await self.send_reminder(channel, event, hours)
    
    @check_reminders.before_loop
    async def before_check_reminders(self):
        """Wait for bot to be ready before starting the loop"""
        await self.bot.wait_until_ready()
        print(f"✅ Reminder checker started! Checking every {Config.CHECK_INTERVAL} minutes")
    
    def should_send_reminder(self, event, hours_before):
        """Check if we should send a reminder now"""
        event_time = datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))
        reminder_time = event_time - timedelta(hours=hours_before)
        now = datetime.now(reminder_time.tzinfo)
        
        # Check if it's time to send (within 5 min window)
        time_diff = (now - reminder_time).total_seconds()
        
        # Create unique key for this reminder
        reminder_key = f"{event['id']}_{hours_before}"
        
        # Send if within 5 minutes and not already sent
        if -300 <= time_diff <= 300 and reminder_key not in self.sent_reminders:
            self.sent_reminders.add(reminder_key)
            return True
        
        return False
    
    async def send_reminder(self, channel, event, hours_before):
        """Send a reminder message for an event"""
        # Load roster based on event title (team name)
        team_name = event.get('title', '').strip()
        roster = self.roster_storage.get_roster(team_name) if team_name else None

        # Get event type from subcalendar
        teamup = TeamUpAPI()
        subcal_ids = event.get('subcalendar_ids', event.get('subcalendar_id'))
        event_type = teamup.get_subcalendar_name(subcal_ids) if subcal_ids else None

        # Create embed with roster and event type if available
        embed = format_event_embed(event, roster=roster, event_type=event_type)
        
        # Create mention string
        mentions = []
        if Config.PLAYER_ROLE_ID:
            mentions.append(f"<@&{Config.PLAYER_ROLE_ID}>")
        if Config.COACH_ROLE_ID:
            mentions.append(f"<@&{Config.COACH_ROLE_ID}>")
        
        mention_text = " ".join(mentions) if mentions else ""
        
        # Get reminder message based on time
        reminder_msg = self.get_reminder_message(hours_before)
        
        # Send reminder
        message_content = f"{reminder_msg}\n{mention_text}"
        
        try:
            await channel.send(content=message_content, embed=embed)
            print(f"✅ Sent {hours_before}h reminder for: {event.get('title', 'Unknown')}")
        except Exception as e:
            print(f"❌ Error sending reminder: {e}")
    
    def get_reminder_message(self, hours_before):
        """Get appropriate reminder message based on time"""
        return "🚨 **EVENT STARTING IN 30 MINUTES**"
    
    @tasks.loop(time=time(hour=12, minute=0))  # Run at noon (12:00 PM) every day
    async def daily_noon_reminder(self):
        """Send daily reminder at noon with today's events and inspirational quote"""
        if not Config.REMINDER_CHANNEL_ID:
            return

        channel = self.bot.get_channel(Config.REMINDER_CHANNEL_ID)
        if not channel:
            print(f"Could not find channel with ID {Config.REMINDER_CHANNEL_ID}")
            return

        # Initialize TeamUp API
        teamup = TeamUpAPI()
        today = datetime.now().strftime('%Y-%m-%d')

        # Get events for today
        events = teamup.get_events(start_date=today, end_date=today)

        # Get a random inspirational quote
        quote = random.choice(INSPIRATIONAL_QUOTES)

        # Create embed
        embed = discord.Embed(
            title="🌅 Good Day, Champions!",
            description=f"*{quote}*",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )

        if events:
            # Get event types and rosters
            event_info = []
            for event in events:
                start_time = datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))
                unix_timestamp = int(start_time.timestamp())

                # Get event type
                subcal_ids = event.get('subcalendar_ids', event.get('subcalendar_id'))
                event_type = teamup.get_subcalendar_name(subcal_ids) if subcal_ids else None

                # Get roster
                team_name = event.get('title', '').strip()
                roster = self.roster_storage.get_roster(team_name) if team_name else None

                # Build event info
                info_parts = [f"**{event.get('title', 'Event')}**"]
                info_parts.append(f"⏰ <t:{unix_timestamp}:t>")
                if event_type:
                    emoji = "🎮"
                    if "warm" in event_type.lower():
                        emoji = "🔥"
                    elif "official" in event_type.lower():
                        emoji = "🏆"
                    elif "vod" in event_type.lower():
                        emoji = "🎥"
                    info_parts.append(f"{emoji} {event_type}")
                if event.get('who'):
                    info_parts.append(f"🆚 {event['who']}")
                if roster:
                    roster_text = ", ".join(roster[:6])
                    if len(roster) > 6:
                        roster_text += f" +{len(roster) - 6} more"
                    info_parts.append(f"👥 {roster_text}")

                event_info.append("\n".join(info_parts))

            embed.add_field(
                name=f"📅 Today's Schedule ({len(events)} event{'s' if len(events) > 1 else ''})",
                value="\n\n".join(event_info),
                inline=False
            )
        else:
            embed.add_field(
                name="📅 Today's Schedule",
                value="No scrims scheduled for today. Use this time to practice and improve! 💪",
                inline=False
            )

        embed.set_footer(text="Let's make today count!")

        # Create mention string
        mentions = []
        if Config.PLAYER_ROLE_ID:
            mentions.append(f"<@&{Config.PLAYER_ROLE_ID}>")
        if Config.COACH_ROLE_ID:
            mentions.append(f"<@&{Config.COACH_ROLE_ID}>")

        mention_text = " ".join(mentions) if mentions else ""

        try:
            await channel.send(content=mention_text, embed=embed)
            print(f"✅ Sent daily noon reminder with {len(events) if events else 0} event(s)")
        except Exception as e:
            print(f"❌ Error sending daily noon reminder: {e}")

    @daily_noon_reminder.before_loop
    async def before_daily_noon_reminder(self):
        """Wait for bot to be ready before starting the daily reminder loop"""
        await self.bot.wait_until_ready()
        print("✅ Daily noon reminder started! Will send at 12:00 PM every day")

    @commands.command(name='forcecheckremind')
    @commands.has_permissions(administrator=True)
    async def force_check(self, ctx):
        """Manually trigger reminder check (Admin only)"""
        await ctx.send("🔄 Forcing reminder check...")
        await self.check_reminders()
        await ctx.send("✅ Reminder check complete!")

    @commands.command(name='forcedaily')
    @commands.has_permissions(administrator=True)
    async def force_daily(self, ctx):
        """Manually trigger daily noon reminder (Admin only)"""
        await ctx.send("🔄 Forcing daily reminder...")
        await self.daily_noon_reminder()
        await ctx.send("✅ Daily reminder sent!")


async def setup(bot):
    await bot.add_cog(Reminders(bot))
