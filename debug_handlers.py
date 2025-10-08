#!/usr/bin/env python3
"""
Debug script to check which handlers are actually registered.
"""

import asyncio
from aiogram import Dispatcher
from bot.core.bot import create_bot, create_dispatcher
from bot.core.middleware import setup_middleware
from bot.handlers import register_handlers

async def debug_handlers():
    """Debug handler registration."""
    print("🔍 Debugging Handler Registration")
    print("=" * 40)
    
    try:
        # Create bot and dispatcher
        bot = create_bot()
        dp = create_dispatcher()
        
        # Setup middleware and handlers
        setup_middleware(dp)
        register_handlers(dp)
        
        # Check message handlers
        print(f"📨 Message handlers: {len(dp.message.handlers)}")
        for i, handler in enumerate(dp.message.handlers):
            filters = getattr(handler, 'filters', 'No filters')
            callback = getattr(handler, 'callback', 'No callback')
            print(f"  {i+1}. {callback.__name__ if hasattr(callback, '__name__') else callback} - {filters}")
        
        # Check callback handlers
        print(f"\n📞 Callback handlers: {len(dp.callback_query.handlers)}")
        for i, handler in enumerate(dp.callback_query.handlers):
            filters = getattr(handler, 'filters', 'No filters')
            callback = getattr(handler, 'callback', 'No callback')
            print(f"  {i+1}. {callback.__name__ if hasattr(callback, '__name__') else callback} - {filters}")
        
        await bot.session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_handlers())
