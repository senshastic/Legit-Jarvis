import discord
from datetime import datetime


def format_event_embed(event, roster=None, event_type=None):
    """
    Create a rich Discord embed for an event

    Args:
        event: Event data dictionary
        roster: Optional list of player names for the roster
        event_type: Optional string for the event type (e.g., "Scrim", "Warmup")
    """
    # Choose emoji based on event type
    emoji = "🎮"
    if event_type:
        type_lower = event_type.lower()
        if "warm" in type_lower:
            emoji = "🔥"
        elif "official" in type_lower:
            emoji = "🏆"
        elif "vod" in type_lower:
            emoji = "🎥"
        elif "scrim" in type_lower:
            emoji = "🎮"

    title = f"{emoji} {event.get('title', 'Event')}"
    if event_type:
        title += f" ({event_type})"

    embed = discord.Embed(
        title=title,
        color=discord.Color.red(),
        timestamp=datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))
    )

    # Parse event details
    start_time = datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(event['end_dt'].replace('Z', '+00:00'))

    # Convert to Unix timestamps for Discord's timezone support
    start_unix = int(start_time.timestamp())
    end_unix = int(end_time.timestamp())

    # Format time using Discord timestamps (shows in user's local timezone)
    embed.add_field(
        name="📅 Date & Time",
        value=f"<t:{start_unix}:F>\n<t:{start_unix}:t> - <t:{end_unix}:t>",
        inline=False
    )

    # Add roster if available
    if roster:
        roster_text = "\n".join(f"• {player}" for player in roster)
        embed.add_field(
            name="👥 Roster",
            value=roster_text,
            inline=False
        )

    # Add notes/description if available
    if event.get('notes'):
        embed.add_field(
            name="📝 Details",
            value=event['notes'][:1024],  # Discord limit
            inline=False
        )

    # Add location/opponent info if in title or notes
    if event.get('location'):
        embed.add_field(
            name="📍 Location/Platform",
            value=event['location'],
            inline=False
        )

    # Add who field if available (opponent team)
    if event.get('who'):
        embed.add_field(
            name="🆚 Opponent",
            value=event['who'],
            inline=False
        )

    # Footer with event ID for tracking
    embed.set_footer(text=f"Event ID: {event['id']}")

    return embed


def format_upcoming_events_embed(events, event_types=None, rosters=None):
    """Create an embed for listing multiple upcoming events

    Args:
        events: List of event dictionaries
        event_types: Optional dictionary mapping event IDs to their types
        rosters: Optional dictionary mapping event IDs to roster lists
    """
    if not events:
        return None

    # Sort by start time
    events.sort(key=lambda x: x['start_dt'])

    embed = discord.Embed(
        title="📋 Upcoming Events",
        color=discord.Color.blue(),
        description=f"Next {len(events)} scheduled event{'s' if len(events) > 1 else ''}"
    )

    for event in events[:10]:  # Limit to 10 events
        start_time = datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))

        # Convert to Unix timestamp for Discord's timezone support
        unix_timestamp = int(start_time.timestamp())

        # Get event type if available
        event_type = event_types.get(event['id']) if event_types else None
        emoji = "🎮"
        if event_type:
            type_lower = event_type.lower()
            if "warm" in type_lower:
                emoji = "🔥"
            elif "official" in type_lower:
                emoji = "🏆"
            elif "vod" in type_lower:
                emoji = "🎥"

        # Create value with optional opponent and type info
        # Use Discord timestamp format for automatic timezone conversion
        value_parts = [f"📅 <t:{unix_timestamp}:F>"]
        if event_type:
            value_parts.append(f"{emoji} Type: {event_type}")
        if event.get('who'):
            value_parts.append(f"🆚 {event['who']}")

        # Add roster if available
        if rosters and event['id'] in rosters:
            roster = rosters[event['id']]
            if roster:
                roster_text = ", ".join(roster[:6])  # Show first 6 players
                if len(roster) > 6:
                    roster_text += f" +{len(roster) - 6} more"
                value_parts.append(f"👥 Roster: {roster_text}")

        embed.add_field(
            name=event.get('title', 'Event'),
            value="\n".join(value_parts),
            inline=False
        )

    return embed


def format_week_events_embed(events, event_types=None, rosters=None):
    """Create an organized embed for week view with events grouped by day

    Args:
        events: List of event dictionaries
        event_types: Optional dictionary mapping event IDs to their types
        rosters: Optional dictionary mapping event IDs to roster lists
    """
    from collections import defaultdict

    if not events:
        return None

    # Sort by start time
    events.sort(key=lambda x: x['start_dt'])

    # Group events by day
    events_by_day = defaultdict(list)
    for event in events:
        start_time = datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))
        day_name = start_time.strftime('%A, %B %d')  # e.g., "Monday, February 17"
        events_by_day[day_name].append(event)

    embed = discord.Embed(
        title="📅 This Week's Schedule",
        color=discord.Color.blue(),
        description=f"Showing {len(events)} upcoming event{'s' if len(events) > 1 else ''}"
    )

    # Add each day as a field
    for day_name, day_events in events_by_day.items():
        event_blocks = []

        for event in day_events:
            start_time = datetime.fromisoformat(event['start_dt'].replace('Z', '+00:00'))
            unix_timestamp = int(start_time.timestamp())

            # Get event type
            event_type = event_types.get(event['id']) if event_types else None
            emoji = "🎮"
            if event_type:
                type_lower = event_type.lower()
                if "warm" in type_lower:
                    emoji = "🔥"
                elif "official" in type_lower:
                    emoji = "🏆"
                elif "vod" in type_lower:
                    emoji = "🎥"

            # Build event block with title and details
            event_text = f"**{event.get('title', 'Event')}** • <t:{unix_timestamp}:t>"

            details = []
            if event_type:
                details.append(f"{emoji} {event_type}")
            if event.get('who'):
                details.append(f"🆚 {event['who']}")

            if details:
                event_text += f"\n{' | '.join(details)}"

            # Add roster on separate line if available
            if rosters and event['id'] in rosters:
                roster = rosters[event['id']]
                if roster:
                    roster_text = ", ".join(roster)
                    event_text += f"\n👥 {roster_text}"

            event_blocks.append(event_text)

        # Add field for this day with clear separation
        embed.add_field(
            name=f"━━━━━━━━━━━━━━━━━━━━━━",
            value="",
            inline=False
        )
        embed.add_field(
            name=f"📆 {day_name}",
            value="\n\n".join(event_blocks),
            inline=False
        )

    embed.set_footer(text="Times shown in your local timezone")

    return embed


def format_bot_info_embed(config):
    """Create an embed showing bot configuration"""
    embed = discord.Embed(
        title="🤖 Bot Configuration",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="Calendar Connected",
        value="✅ Yes" if config.get('calendar_connected') else "❌ No",
        inline=True
    )
    embed.add_field(
        name="Reminder Channel",
        value=f"<#{config.get('reminder_channel_id')}>" if config.get('reminder_channel_id') else "❌ Not Set",
        inline=True
    )
    embed.add_field(
        name="Check Interval",
        value=config.get('check_interval', 'Every 5 minutes'),
        inline=True
    )
    embed.add_field(
        name="Reminder Times",
        value=config.get('reminder_times', 'Not configured'),
        inline=False
    )
    embed.add_field(
        name="Player Role",
        value=f"<@&{config.get('player_role_id')}>" if config.get('player_role_id') else "❌ Not Set",
        inline=True
    )
    embed.add_field(
        name="Coach Role",
        value=f"<@&{config.get('coach_role_id')}>" if config.get('coach_role_id') else "❌ Not Set",
        inline=True
    )
    
    return embed
