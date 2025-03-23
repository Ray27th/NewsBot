import asyncio
import datetime
from dotenv import load_dotenv
import os

from fastapi.responses import RedirectResponse, HTMLResponse

from app_instance import app
from discord_bot import discord_bot
from log_handler import logger
from schedule_handler import sgt
from supabase_handler import start_realtime_listener, get_data_after_date
from telegram_bot import telegram_bot, dp

# Setup .env file
load_dotenv()

app.state.news_data = []


@app.on_event("startup")
async def startup() -> None:
    # Clear Logs
    clear_logs()

    # Start Discord Bot
    asyncio.create_task(discord_bot.start(os.environ["DISCORD_BOT"]))

    # Start Telegram Bot
    logger(
        f"[System] Telegram Bot logged in as {(await telegram_bot.get_my_name()).name}"
    )
    asyncio.create_task(dp.start_polling(telegram_bot))

    # Start Supabase Realtime Listener
    start_realtime_listener()

    # Get news data
    now = datetime.datetime.now(sgt)
    app.state.news_data = get_data_after_date(now.isoformat())


### === FASTAPI ROUTES === ###
@app.get("/")
def start():
    logger(f"[Data] {app.state.news_data}")
    return {"message": "Bots are active!"}


@app.get("/logs", response_class=HTMLResponse)
def get_logs():
    with open("logs.log", "r") as f:
        data = f.read()
    formatted_content = f"""
    <html>
        <head>
            <meta http-equiv="refresh" content="30">
        </head>
        <body>
            <a href="/clear">Clear Logs</a>
            <pre>{data}</pre>
        </body>
    </html>
    """
    return formatted_content


@app.get("/clear", response_class=RedirectResponse)
def clear():
    clear_logs()
    return "/logs"


def clear_logs():
    with open("logs.log", "w") as f:
        f.write("")
    logger("[System] Logger Starting Up......")
