import datetime

from discord.ext import tasks
import pytz

from app_instance import app
from supabase_handler import get_data_after_date
from telegram_bot import send_message_to_chat, TELEGRAM_CHAT_ID

# Define Singapore Timezone
sgt = pytz.timezone("Asia/Singapore")

target_time = datetime.datetime.now(sgt).replace(
    hour=21, minute=56, second=0, microsecond=0
)

midnight_time = datetime.datetime.now(sgt).replace(
    hour=0, minute=0, second=0, microsecond=0
)


### === DISCORD & TELEGRAM SCHEDULED TASK === ###
@tasks.loop(minutes=1)
async def tasks_loop():
    """Runs every minute and checks if the current time matches the scheduled time."""
    now = datetime.datetime.now(sgt)

    # Update news data every midnight
    if now.hour == midnight_time.hour and now.minute == midnight_time.minute:
        app.state.news_data = get_data_after_date(now.isoformat())

    if (
        now.hour == target_time.hour
        and now.minute == target_time.minute
        and len(app.state.news_data) > 0
    ):
        from discord_bot import (
            discord_bot,
            FORUM_CHANNEL_ID,
        )  # Import here to avoid circular dependency

        print("[System] Scheduled Task Executed for Discord and Telegram")

        # Send Telegram Message
        await send_message_to_chat(
            TELEGRAM_CHAT_ID, "NEW Scheduled Post🚀 Automated Message!"
        )

        # Send Discord Message
        forum_channel = discord_bot.get_channel(FORUM_CHANNEL_ID)
        if forum_channel:
            await forum_channel.create_thread(
                name="NEW Scheduled Post", content="🚀 Automated Message!"
            )
