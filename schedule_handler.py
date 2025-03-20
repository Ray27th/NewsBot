from discord.ext import tasks
from telegram_bot import TELEGRAM_CHAT_ID, send_message_to_chat
import pytz
import datetime

# Define Singapore Timezone
sgt = pytz.timezone("Asia/Singapore")

target_time = datetime.datetime.now(sgt).replace(
    hour=21, minute=56, second=0, microsecond=0
)


### === DISCORD & TELEGRAM SCHEDULED TASK === ###
@tasks.loop(minutes=1)
async def tasks_loop():
    """Runs every minute and checks if the current time matches the scheduled time."""
    now = datetime.datetime.now(sgt)

    if now.hour == target_time.hour and now.minute == target_time.minute:
        from discord_bot import (
            discord_bot,
            FORUM_CHANNEL_ID,
        )  # Import here to avoid circular dependency

        # Send Telegram Message
        await send_message_to_chat(
            TELEGRAM_CHAT_ID, "NEW Scheduled Post🚀 Automated Message!"
        )
        print(
            "Scheduled Task Executed for Discord and Telegram"
        )  # Replaced logger to avoid circular issue

        # Send Discord Message
        forum_channel = discord_bot.get_channel(FORUM_CHANNEL_ID)
        if forum_channel:
            await forum_channel.create_thread(
                name="NEW Scheduled Post", content="🚀 Automated Message!"
            )
