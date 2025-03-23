import os

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import (
    ChatMemberUpdatedFilter,
    CommandStart,
    IS_MEMBER,
    IS_NOT_MEMBER,
)
from aiogram.types import ChatMemberUpdated, Message

from log_handler import logger

# Telegram Bot Setup
dp = Dispatcher()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT")
TELEGRAM_CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])
telegram_bot = Bot(
    token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="MarkdownV2")
)


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


# @dp.message()
# async def echo_handler(message: Message) -> None:
#     logger(f"[Telegram Message] {message.from_user.username}: {message.text}")
#     if (
#         message.from_user.id == (await telegram_bot.me()).id
#     ):  # Ignore messages from the bot itself
#         return

#     try:
#         await message.send_copy(chat_id=message.chat.id)
#         await send_message_to_chat(message.chat.id, message.text)
#         await send_message_to_chat(TELEGRAM_CHAT_ID, "This is just a repeat test")
#     except Exception as e:
#         logger(f"[Telegram] Error occurred at `on_message` function: {e}", "ERROR")


async def send_message_to_chat(
    chat_id: int, message: str, message_thread_id: int = None
):
    """Send a message to a specific Telegram chat."""
    try:
        logger(
            f"[Telegram Message] {(await telegram_bot.get_my_name()).name}: {message}"
        )
        await telegram_bot.send_message(
            chat_id=chat_id, text=message, message_thread_id=message_thread_id
        )
    except Exception as e:
        logger(e, "ERROR")
