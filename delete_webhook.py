#!/usr/bin/env python3
"""
Delete Telegram webhook to enable polling mode.
"""

import asyncio
import logging
from bot.core.bot import create_bot
from bot.core.logging import setup_logging

logger = logging.getLogger(__name__)

async def main():
    """Delete the webhook."""
    setup_logging()
    
    logger.info("🔧 Deleting Telegram webhook...")
    
    try:
        bot = create_bot()
        
        # Delete webhook
        await bot.delete_webhook(drop_pending_updates=True)
        
        logger.info("✅ Webhook deleted successfully!")
        logger.info("🤖 You can now start the bot in polling mode")
        
        # Close bot session
        await bot.session.close()
        
    except Exception as e:
        logger.error(f"❌ Failed to delete webhook: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    asyncio.run(main())
