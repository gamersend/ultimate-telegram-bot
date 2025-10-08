#!/usr/bin/env python3
"""
Set bot commands with Telegram BotFather.
This registers the commands so they appear in the Telegram UI.
"""

import asyncio
import logging
from aiogram.types import BotCommand
from bot.core.bot import create_bot

logger = logging.getLogger(__name__)

async def set_bot_commands():
    """Set bot commands with Telegram."""
    print("🔧 Setting Bot Commands with Telegram")
    print("=" * 45)
    
    try:
        bot = create_bot()
        
        # Define all bot commands
        commands = [
            # Basic commands
            BotCommand(command="start", description="🚀 Start the bot and see features"),
            BotCommand(command="help", description="❓ Show help and command list"),
            BotCommand(command="status", description="📊 Show bot status"),
            
            # AI commands
            BotCommand(command="ask", description="🧠 Ask AI anything"),
            BotCommand(command="explain", description="📚 Get detailed explanations"),
            BotCommand(command="code", description="💻 Get programming help"),
            BotCommand(command="summarize", description="📝 Summarize text"),
            BotCommand(command="generate", description="🎨 Generate images"),
            
            # Fun commands
            BotCommand(command="meme", description="😂 Get random memes"),
            BotCommand(command="joke", description="🤣 Get random jokes"),
            BotCommand(command="fact", description="🤓 Get fun facts"),
            BotCommand(command="trivia", description="🧠 Play trivia games"),
            BotCommand(command="gif", description="🎬 Search for GIFs"),
            
            # Finance commands
            BotCommand(command="stock", description="📈 Get stock prices"),
            BotCommand(command="crypto", description="₿ Get crypto prices"),
            BotCommand(command="market", description="📊 Market overview"),
            
            # News commands
            BotCommand(command="news", description="📰 Latest news"),
            BotCommand(command="feeds", description="📡 RSS feeds"),
            
            # Notes commands
            BotCommand(command="note", description="📝 Create and manage notes"),
            BotCommand(command="files", description="📁 File management"),
            
            # Media commands
            BotCommand(command="download", description="⬇️ Download YouTube videos"),
            BotCommand(command="spotify", description="🎵 Spotify control"),
            
            # Voice commands
            BotCommand(command="tts", description="🗣️ Text to speech"),
            
            # Image commands
            BotCommand(command="sd", description="🎨 Stable Diffusion images"),
            BotCommand(command="edit", description="✏️ Edit images"),
            BotCommand(command="upscale", description="🔍 Upscale images"),
            
            # Smart home commands (if configured)
            BotCommand(command="lights", description="💡 Control lights"),
            BotCommand(command="scene", description="🏠 Activate scenes"),
            BotCommand(command="temp", description="🌡️ Check temperature"),
            BotCommand(command="home", description="🏠 Home status"),
            
            # Tesla commands (if configured)
            BotCommand(command="tesla", description="🚗 Tesla vehicle control"),
            BotCommand(command="climate", description="❄️ Climate control"),
            BotCommand(command="charge", description="🔋 Charging control"),
        ]
        
        # Set commands with Telegram
        await bot.set_my_commands(commands)
        
        print(f"✅ Successfully set {len(commands)} commands with Telegram!")
        print("\nRegistered commands:")
        for cmd in commands:
            print(f"   /{cmd.command} - {cmd.description}")
        
        # Verify commands were set
        registered_commands = await bot.get_my_commands()
        print(f"\n🔍 Verification: {len(registered_commands)} commands registered")
        
        await bot.session.close()
        
        print(f"\n🎉 Bot commands are now available in Telegram!")
        print("💡 Commands will appear in the Telegram UI when you type '/'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting commands: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(set_bot_commands())
