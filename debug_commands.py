#!/usr/bin/env python3
"""
Debug script to test specific commands manually.
"""

import asyncio
import logging
from bot.core.bot import create_bot
from bot.config import settings

logger = logging.getLogger(__name__)

async def test_specific_commands():
    """Test specific commands that might be failing."""
    print("🔍 Testing Specific Commands")
    print("=" * 40)
    
    try:
        bot = create_bot()
        
        # Test bot commands
        commands = await bot.get_my_commands()
        print(f"✅ Bot has {len(commands)} registered commands:")
        for cmd in commands:
            print(f"   /{cmd.command} - {cmd.description}")
        
        # Test webhook info
        webhook_info = await bot.get_webhook_info()
        print(f"\n🔗 Webhook URL: {webhook_info.url or 'None (polling mode)'}")
        print(f"📊 Pending updates: {webhook_info.pending_update_count}")
        
        await bot.session.close()
        
        print(f"\n💡 If commands aren't working, try:")
        print("1. Restart the bot")
        print("2. Clear Telegram cache")
        print("3. Check bot logs for errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_specific_commands())
