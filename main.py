from log_handler import logger

import asyncio
import datetime
from dotenv import load_dotenv
import logging
import os
import pytz
import threading

import aiocron
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import ChatMemberUpdatedFilter, CommandStart, IS_MEMBER, IS_NOT_MEMBER
from aiogram.types import ChatMemberUpdated, Message
import discord
from discord.ext import commands, tasks
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse

# Setup
load_dotenv()

# Define Singapore Timezone
sgt = pytz.timezone("Asia/Singapore")

app = FastAPI()

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
command_prefix = "/"
discord_bot = commands.Bot(command_prefix=command_prefix, intents=intents)
FORUM_CHANNEL_ID = int(os.environ["FORUM_CHANNEL_ID"])

# Telegram Bot Setup
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT")
TELEGRAM_CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

target_time = datetime.datetime.now(sgt).replace(hour=23, minute=55, second=0, microsecond=0)


@app.on_event("startup")
async def startup():
    # Clear Logs
    with open('logs.log', 'w') as f:
        pass

    # Start Discord Bot
    asyncio.create_task(discord_bot.start(os.environ["DISCORD_BOT"]))

    asyncio.create_task(dp.start_polling(telegram_bot))


### === DISCORD BOT EVENTS === ###
@discord_bot.event
async def on_ready():
    logger(f"[System] Discord Bot logged in as {discord_bot.user}")

    # Start the scheduled task
    if not tasks_loop.is_running():
        tasks_loop.start()
        logger("[System] Scheduled task started.")


@discord_bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")


@discord_bot.event
async def on_message(message):
    try:
        logger(f"[Message] {message.author}: {message.content}")
        if message.author.bot:  # Ignore bot messages
            return

        if message.content.startswith(command_prefix):
            # Ensure commands are processed
            await discord_bot.process_commands(message)
    except:
        logger("Error occurred at `on_message` function", "ERROR")


### === TELEGRAM BOT COMMAND HANDLERS === ###
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def greet_new_member(event: ChatMemberUpdated):
    new_user = event.new_chat_member.user
    chat_id = event.chat.id

    welcome_message = f"Welcome, {new_user.mention_html()}! 👋 We're glad you're here."
    
    # Send welcome message
    await telegram_bot.send_message(chat_id, welcome_message)

@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        await message.send_copy(chat_id=message.chat.id)
        await send_message_to_chat(TELEGRAM_CHAT_ID, "NEW Scheduled Post🚀 Automated Message!")
    except TypeError:
        await message.answer("Nice try!")

async def send_message_to_chat(chat_id: int, message: str):
    """Send a message to a specific Telegram chat."""
    logger(f"YOU TRIED {chat_id}")
    await telegram_bot.send_message(chat_id=chat_id, text=message,message_thread_id=2)

### === DISCORD & TELEGRAM SCHEDULED TASK === ###
@tasks.loop(minutes=1)
async def tasks_loop():
    """Runs every minute and checks if the current time matches the scheduled time."""
    now = datetime.datetime.now(sgt)
    if now.hour == target_time.hour and now.minute == target_time.minute:

        # Send Telegram Message
        await send_message_to_chat(TELEGRAM_CHAT_ID, "NEW Scheduled Post🚀 Automated Message!")
        logger("Scheduled Task Executed for Discord and Telegram")

        # Send Discord Message
        forum_channel = discord_bot.get_channel(FORUM_CHANNEL_ID)
        if forum_channel:
            await forum_channel.create_thread(name="NEW Scheduled Post", content="🚀 Automated Message!")


### === FASTAPI ROUTES === ###
@app.get("/")
def start():
    return {"message": "Bots are active!"}


@app.get("/logs", response_class=HTMLResponse)
def get_logs():
    with open("logs.log",'r') as f:
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
    """ # Preserves formatting
    return formatted_content

@app.get("/clear-logs", response_class=RedirectResponse)
def clear_logs():
    with open("logs.log",'w') as f:
        f.write("")
    return "/logs"

@discord_bot.command()
async def create_forum_post(ctx, title: str, *, content: str):
    """Creates a forum post in a specific forum channel."""
    forum_channel = discord_bot.get_channel(FORUM_CHANNEL_ID)

    if not isinstance(forum_channel, discord.ForumChannel):
        await ctx.send("The specified channel is not a forum channel!")
        return

    try:
        thread = await forum_channel.create_thread(name=title, content=content)
        await ctx.send(f"✅ Forum post created: {thread.jump_url}")
    except discord.Forbidden:
        await ctx.send("❌ Bot lacks permissions to create forum posts.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Failed to create post: {e}")



### === TELEGRAM BOT STARTUP FUNCTION === ###
