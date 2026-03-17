import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
from embeds import format_event_embed
from roster_storage import RosterStorage
from config import Config
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
    """Automatic reminder system for scrims — runs for every configured team."""

    def __init__(self, bot):
        self.bot = bot
        self.sent_reminders = set()
        self.roster_storage = RosterStorage()
        self.check_reminders.start()
        self.daily_noon_reminder.start()

    def cog_unload(self):
        self.check_reminders.cancel()
        self.daily_noon_reminder.cancel()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def should_send_reminder(self, team_id: str, event: dict, hours_before: float) -> bool:
        event_time = datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))
        reminder_time = event_time - timedelta(hours=hours_before)
        now = datetime.now(reminder_time.tzinfo)
        time_diff = (now - reminder_time).total_seconds()
        key = f"{team_id}_{event['id']}_{hours_before}"
        if -300 <= time_diff <= 300 and key not in self.sent_reminders:
            self.sent_reminders.add(key)
            return True
        return False

    async def send_reminder(self, channel, team, event, hours_before):
        calendar = team.get_calendar()
        team_name = event.get('team_name') or event.get('title', '').strip()
        roster = self.roster_storage.get_roster(team_name) if team_name else None
        event_type = calendar.get_event_type(event)

        embed = format_event_embed(event, roster=roster, event_type=event_type)

        mentions = []
        if team.player_role_id:
            mentions.append(f"<@&{team.player_role_id}>")
        if team.coach_role_id:
            mentions.append(f"<@&{team.coach_role_id}>")
        mention_text = " ".join(mentions)

        try:
            await channel.send(
                content=f"🚨 **EVENT STARTING IN 30 MINUTES**\n{mention_text}",
                embed=embed
            )
            print(f"✅ [{team.name}] Sent reminder for: {event.get('title', 'Unknown')}")
        except Exception as e:
            print(f"❌ [{team.name}] Error sending reminder: {e}")

    # ------------------------------------------------------------------
    # Background tasks
    # ------------------------------------------------------------------

    @tasks.loop(minutes=Config.CHECK_INTERVAL)
    async def check_reminders(self):
        """Check for upcoming events across all teams and send reminders."""
        for team in self.bot.team_manager.get_all_teams():
            if not team.reminder_channel_id:
                continue
            channel = self.bot.get_channel(team.reminder_channel_id)
            if not channel:
                continue
            try:
                calendar = team.get_calendar()
                events = calendar.get_upcoming_events(days=7)
            except Exception as e:
                print(f"❌ [{team.name}] Calendar error: {e}")
                continue

            for event in events:
                for hours in Config.REMINDER_TIMES:
                    if self.should_send_reminder(team.team_id, event, hours):
                        await self.send_reminder(channel, team, event, hours)

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()
        print(f"✅ Reminder checker started (every {Config.CHECK_INTERVAL} min)")

    @tasks.loop(time=time(hour=12, minute=0))
    async def daily_noon_reminder(self):
        """Send daily noon summary to each team's reminder channel."""
        for team in self.bot.team_manager.get_all_teams():
            if not team.reminder_channel_id:
                continue
            channel = self.bot.get_channel(team.reminder_channel_id)
            if not channel:
                continue
            try:
                await self._send_daily_summary(channel, team)
            except Exception as e:
                print(f"❌ [{team.name}] Daily reminder error: {e}")

    @daily_noon_reminder.before_loop
    async def before_daily_noon_reminder(self):
        await self.bot.wait_until_ready()
        print("✅ Daily noon reminder started (12:00 PM daily)")

    async def _send_daily_summary(self, channel, team):
        calendar = team.get_calendar()
        today = datetime.now().strftime('%Y-%m-%d')
        events = calendar.get_events(start_date=today, end_date=today)
        quote = random.choice(INSPIRATIONAL_QUOTES)

        embed = discord.Embed(
            title="🌅 Good Day, Champions!",
            description=f"*{quote}*",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )

        if events:
            event_info = []
            for event in events:
                start_time = datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))
                unix_timestamp = int(start_time.timestamp())
                event_type = calendar.get_event_type(event)

                display_name = event.get('team_name') or event.get('title', 'Event')
                roster = self.roster_storage.get_roster(display_name) if display_name else None
                info_parts = [f"**{display_name}**"]
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

        mentions = []
        if team.player_role_id:
            mentions.append(f"<@&{team.player_role_id}>")
        if team.coach_role_id:
            mentions.append(f"<@&{team.coach_role_id}>")
        mention_text = " ".join(mentions)

        await channel.send(content=mention_text, embed=embed)
        print(f"✅ [{team.name}] Daily summary sent ({len(events) if events else 0} event(s))")

    # ------------------------------------------------------------------
    # Manual trigger commands
    # ------------------------------------------------------------------

    @commands.command(name='forcecheckremind')
    @commands.has_permissions(administrator=True)
    async def force_check(self, ctx):
        team = self.bot.team_manager.get_team_for_guild(ctx.guild.id)
        if not team:
            return await ctx.send("❌ This server is not configured in `teams.json`.")
        await ctx.send("🔄 Forcing reminder check...")
        channel = self.bot.get_channel(team.reminder_channel_id)
        if channel:
            try:
                calendar = team.get_calendar()
                events = calendar.get_upcoming_events(days=7)
                for event in events:
                    for hours in Config.REMINDER_TIMES:
                        if self.should_send_reminder(team.team_id, event, hours):
                            await self.send_reminder(channel, team, event, hours)
            except Exception as e:
                await ctx.send(f"❌ Calendar error: {e}")
                return
        await ctx.send("✅ Reminder check complete!")

    @commands.command(name='forcedaily')
    @commands.has_permissions(administrator=True)
    async def force_daily(self, ctx):
        team = self.bot.team_manager.get_team_for_guild(ctx.guild.id)
        if not team:
            return await ctx.send("❌ This server is not configured in `teams.json`.")
        await ctx.send("🔄 Forcing daily reminder...")
        channel = self.bot.get_channel(team.reminder_channel_id)
        if channel:
            try:
                await self._send_daily_summary(channel, team)
            except Exception as e:
                await ctx.send(f"❌ Error: {e}")
                return
        await ctx.send("✅ Daily reminder sent!")


async def setup(bot):
    await bot.add_cog(Reminders(bot))
