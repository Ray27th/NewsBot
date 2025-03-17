from log_handler import logger

import discord
from discord.ext import commands, tasks
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, HTMLResponse
import asyncio
import aiocron

import logging
import datetime
import os
from dotenv import load_dotenv

# Setup
load_dotenv()

utc = datetime.timezone.utc

app = FastAPI()

# Set up bot with a prefix
intents = discord.Intents.default()
intents.message_content = True

command_prefix = "/"
bot = commands.Bot(command_prefix=command_prefix, intents=intents)

@app.on_event("startup")
async def startup():
    # Create file first
    with open('logs.log', 'w') as f:
        f.write("")
    asyncio.create_task(bot.start(os.environ["DISCORD_BOT"]))


# Event: Bot is ready
@bot.event
async def on_ready():
    logger(f"[System] Bot logged in as {bot.user}")


# Command: !hello
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")


# Command: !add <number1> <number2>
@bot.command()
async def add(ctx, num1: int, num2: int):
    result = num1 + num2
    await ctx.send(f"The sum of {num1} and {num2} is {result}.")


# Event: Responding to specific keywords
@bot.event
async def on_message(message):
    try:
        logger(f"[User Message] {message.author}: {message.content}")
        if message.author.bot:  # Ignore bot messages
            return

        if message.content.startswith(command_prefix):
            # Ensure commands are processed
            await bot.process_commands(message)

        if "pycord" in message.content.lower():
            await message.channel.send("Pycord is awesome! 🚀")
    except:
        logger("Error occurred at `on_message` function", "ERROR")



@app.get("/")
def start():
    return {"message": "Bot is active!"}


@app.get("/logs", response_class=HTMLResponse)
def get_logs():
    with open("logs.log",'r') as f:
        data = f.read()
    formatted_content = "<pre>" + data + "</pre>"  # Preserves formatting
    return formatted_content

@app.get("/clearlogs", response_class=RedirectResponse)
def clear_logs():
    with open("logs.log",'w') as f:
        f.write("")
    return "/logs"

BOT_CHANNELS = int(os.environ["BOT_CHANNEL"])
print(BOT_CHANNELS)

# @aiocron.crontab("* * * * * */20")
# async def HelloWorld():
#     await bot.get_channel(BOT_CHANNELS).send("Hello World!")


# time = datetime.time(hour=8, minute=30, tzinfo=utc)

# @tasks.loop(time=time)
# async def tasks():
#     print("task")
