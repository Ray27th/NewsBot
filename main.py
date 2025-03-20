from discord_bot import discord_bot
from log_handler import logger
from telegram_bot import telegram_bot, dp

import asyncio
from dotenv import load_dotenv
import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse

from supabase_handler import response

# Setup .env file
load_dotenv()

app = FastAPI()


@app.on_event("startup")
async def startup():
    # Clear Logs

    with open("logs.log", "w"):
        pass
    logger("[System] Logger Starting Up......")

    # Start Discord Bot

    asyncio.create_task(discord_bot.start(os.environ["DISCORD_BOT"]))

    # Start Telegram Bot

    logger(
        f"[System] Telegram Bot logged in as {(await telegram_bot.get_my_name()).name}"
    )
    asyncio.create_task(dp.start_polling(telegram_bot))


### === FASTAPI ROUTES === ###
@app.get("/")
def start():
    print(response)
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
            <a href="/clear-logs">Clear Logs</a>
            <pre>{data}</pre>
        </body>
    </html>
    """
    return formatted_content


@app.get("/clear-logs", response_class=RedirectResponse)
def clear_logs():
    with open("logs.log", "w") as f:
        f.write("")
    return "/logs"


# @discord_bot.command()
# async def create_forum_post(ctx, title: str, *, content: str):
#     """Creates a forum post in a specific forum channel."""
#     forum_channel = discord_bot.get_channel(FORUM_CHANNEL_ID)

#     if not isinstance(forum_channel, discord.ForumChannel):
#         await ctx.send("The specified channel is not a forum channel!")
#         return

#     try:
#         thread = await forum_channel.create_thread(name=title, content=content)
#         await ctx.send(f"✅ Forum post created: {thread.jump_url}")
#     except discord.Forbidden:
#         await ctx.send("❌ Bot lacks permissions to create forum posts.")
#     except discord.HTTPException as e:
#         await ctx.send(f"❌ Failed to create post: {e}")
