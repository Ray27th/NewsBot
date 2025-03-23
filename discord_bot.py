import os

import discord
from discord.ext import commands

from log_handler import logger
from schedule_handler import tasks_loop


# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
command_prefix = "/"
FORUM_CHANNEL_ID = int(os.environ["FORUM_CHANNEL_ID"])
discord_bot = commands.Bot(command_prefix=command_prefix, intents=intents)


### === DISCORD BOT EVENTS === ###
@discord_bot.event
async def on_ready():
    logger(f"[System] Discord Bot logged in as {discord_bot.user}")

    # Start the scheduled task
    if not tasks_loop.is_running():
        tasks_loop.start()
        logger("[System] Scheduled task started")


@discord_bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}! POKEMON")


@discord_bot.event
async def on_message(message):
    try:
        logger(f"[Discord Message] {message.author}: {message.content}")
        if message.author.bot:  # Ignore bot messages
            return

        if message.content.startswith(command_prefix):
            # Ensure commands are processed
            await discord_bot.process_commands(message)
    except Exception as e:
        logger(f"[Telegram] Error occurred at `on_message` function: {e}", "ERROR")
