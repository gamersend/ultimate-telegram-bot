#!/usr/bin/env python3
"""
Simple polling mode starter for Ultimate Telegram Bot
This bypasses webhook issues and starts the bot in polling mode.
"""

import asyncio
import logging
from bot.core.bot import create_bot, create_dispatcher
from bot.core.logging import setup_logging
from bot.core.middleware import setup_middleware
from bot.handlers import register_handlers
from bot.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Start the bot in polling mode."""
    # Setup logging
    setup_logging()

    logger.info("🤖 Starting Ultimate Telegram Bot in polling mode...")

    try:
        # Create bot and dispatcher
        bot = create_bot()
        dp = create_dispatcher()

        # Setup middleware
        setup_middleware(dp)

        # Register handlers
        register_handlers(dp)

        # Start polling
        logger.info("🚀 Bot started successfully! Listening for messages...")
        logger.info("📱 Send /start to your bot to test it")
        logger.info("🛑 Press Ctrl+C to stop the bot")

        await dp.start_polling(bot)

    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        return 1

    return 0

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
