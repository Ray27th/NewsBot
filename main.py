import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from fastapi import FastAPI
import asyncio

load_dotenv()

app = FastAPI()

# Set up bot with a prefix
intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@app.on_event("startup")
async def startup():
    asyncio.create_task(bot.start(os.environ["DISCORD_BOT"]))


# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")


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
    print(message)
    if message.author.bot:  # Ignore bot messages
        return

    await message.channel.send(message.author)

    if "pycord" in message.content.lower():
        await message.channel.send("Pycord is awesome! 🚀")

    # Ensure commands are processed
    await bot.process_commands(message)


@app.get("/")
def start():
    return {"Hello": "World"}
