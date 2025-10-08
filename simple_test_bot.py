#!/usr/bin/env python3
"""
Simple test bot to verify basic functionality.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from bot.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create bot and dispatcher
bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: Message):
    """Simple start handler."""
    logger.info(f"START command received from {message.from_user.id}")
    await message.answer("✅ Simple start handler working!")

@dp.message(Command("test"))
async def test_handler(message: Message):
    """Simple test handler."""
    logger.info(f"TEST command received from {message.from_user.id}")
    await message.answer("✅ Simple test handler working!")

@dp.message(Command("debug"))
async def debug_handler(message: Message):
    """Debug handler."""
    logger.info(f"DEBUG command received from {message.from_user.id}")
    user_id = message.from_user.id
    allowed = settings.allowed_user_ids
    await message.answer(f"✅ Debug info:\nUser ID: {user_id}\nAllowed: {allowed}\nAuthorized: {user_id in allowed}")

async def main():
    """Start the simple test bot."""
    logger.info("🧪 Starting Simple Test Bot...")
    logger.info(f"Allowed users: {settings.allowed_user_ids}")
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
