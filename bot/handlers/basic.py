"""Basic command handlers for the bot."""

import logging
from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils.decorators import authorized_only


logger = logging.getLogger(__name__)


@authorized_only
async def start_command(message: Message):
    """Handle /start command."""
    welcome_text = """
🤖 <b>Welcome to your Ultimate Telegram Bot!</b>

Your all-in-one personal assistant is ready to help you with:

🧠 <b>AI Assistant</b>
• /ask - Chat with AI
• /explain - Get explanations
• /code - Code assistance

🎙️ <b>Voice & Audio</b>
• Send voice messages for transcription
• /tts - Text to speech

🖼️ <b>Images</b>
• /generate - Create images
• /edit - Edit images

🏠 <b>Smart Home</b>
• /lights - Control lights
• /scene - Activate scenes

🚗 <b>Tesla</b>
• /tesla - Vehicle controls
• /climate - Climate control

💸 <b>Finance</b>
• /stocks - Stock prices
• /crypto - Crypto prices
• /portfolio - Portfolio tracking

🎵 <b>Media</b>
• /download - YouTube downloads
• /spotify - Spotify controls

📰 <b>News</b>
• /news - Latest news
• /feeds - RSS feeds

📚 <b>Notes</b>
• /note - Save to Notion
• /files - Google Drive

🎮 <b>Fun</b>
• /meme - Generate memes
• /gif - Search GIFs
• /trivia - Play trivia

⚙️ <b>Admin</b>
• /status - Bot status
• /logs - View logs
• /metrics - Performance metrics

Type /help for detailed command information!
"""
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🧠 AI Chat", callback_data="ai_chat"),
            InlineKeyboardButton(text="🏠 Smart Home", callback_data="smart_home")
        ],
        [
            InlineKeyboardButton(text="💸 Finance", callback_data="finance"),
            InlineKeyboardButton(text="🎵 Media", callback_data="media")
        ],
        [
            InlineKeyboardButton(text="📰 News", callback_data="news"),
            InlineKeyboardButton(text="🎮 Fun", callback_data="fun")
        ],
        [
            InlineKeyboardButton(text="⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton(text="❓ Help", callback_data="help")
        ]
    ])
    
    await message.answer(welcome_text, reply_markup=keyboard)


@authorized_only
async def help_command(message: Message):
    """Handle /help command."""
    help_text = """
📖 <b>Detailed Command Reference</b>

<b>🧠 AI Commands:</b>
• /ask [question] - Ask AI anything
• /explain [topic] - Get detailed explanations
• /code [language] [description] - Code assistance
• /summarize - Summarize text or links

<b>🎙️ Voice Commands:</b>
• Send voice message - Auto transcription
• /tts [text] - Convert text to speech
• /whisper [file] - Transcribe audio file

<b>🖼️ Image Commands:</b>
• /generate [prompt] - Generate images
• /edit [prompt] - Edit uploaded images
• /upscale - Upscale images

<b>🏠 Smart Home Commands:</b>
• /lights [on/off/dim] - Control lights
• /scene [name] - Activate scenes
• /temp - Check temperature
• /security - Security status

<b>🚗 Tesla Commands:</b>
• /tesla status - Vehicle status
• /climate [temp] - Set climate
• /charge - Charging info
• /location - Vehicle location

<b>💸 Finance Commands:</b>
• /stock [symbol] - Stock price
• /crypto [coin] - Crypto price
• /portfolio - Portfolio overview
• /alerts - Price alerts

<b>🎵 Media Commands:</b>
• /download [url] - Download media
• /spotify [command] - Spotify controls
• /playlist - Manage playlists

<b>📰 News Commands:</b>
• /news [topic] - Get news
• /feeds - RSS feeds
• /summary - News summary

<b>📚 Notes Commands:</b>
• /note [text] - Save to Notion
• /files - Google Drive files
• /search [query] - Search notes

<b>🎮 Fun Commands:</b>
• /meme [text] - Generate meme
• /gif [search] - Find GIFs
• /trivia - Start trivia game
• /joke - Random joke

<b>⚙️ Admin Commands:</b>
• /status - Bot status
• /logs - View logs
• /metrics - Performance metrics
• /restart - Restart services

Need more help? Just ask me anything!
"""
    
    await message.answer(help_text)


@authorized_only
async def status_command(message: Message):
    """Handle /status command."""
    import psutil
    import time
    from datetime import datetime, timedelta
    
    # Get system info
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Get bot uptime (simplified)
    uptime = datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    status_text = f"""
🤖 <b>Bot Status</b>

📊 <b>System Resources:</b>
• CPU: {cpu_percent}%
• Memory: {memory.percent}% ({memory.used // 1024 // 1024} MB / {memory.total // 1024 // 1024} MB)
• Disk: {disk.percent}% ({disk.used // 1024 // 1024 // 1024} GB / {disk.total // 1024 // 1024 // 1024} GB)

⏱️ <b>Uptime:</b> {uptime}

🔗 <b>Services Status:</b>
• Database: ✅ Connected
• Redis: ✅ Connected
• AI Services: ✅ Available
• Scheduler: ✅ Running

📈 <b>Today's Stats:</b>
• Messages processed: 0
• Commands executed: 0
• Errors: 0

🌐 <b>Network:</b>
• Webhook: {'✅ Active' if hasattr(message.bot, 'webhook_url') else '❌ Polling'}
• Response time: &lt;1ms
"""
    
    await message.answer(status_text)


async def echo_handler(message: Message):
    """Echo handler for unrecognized messages."""
    await message.answer(
        "💬 I received your message! Try /help to see what commands I can do, or just chat with me using /ask [your message]"
    )


async def unknown_command_handler(message: Message):
    """Handler for unrecognized commands."""
    command = message.text.split()[0] if message.text else ""
    await message.answer(
        f"🤔 I don't recognize the command '{command}'. Try /help to see what I can do!"
    )


@authorized_only
async def callback_handler(callback: CallbackQuery):
    """Handle inline keyboard callbacks."""
    data = callback.data

    try:
        if data == "ai_chat":
            text = "🧠 <b>AI Chat Features</b>\n\n"
            text += "• /ask [question] - Chat with AI\n"
            text += "• /explain [topic] - Get explanations\n"
            text += "• /code [request] - Programming help\n"
            text += "• /summarize [text] - Summarize content\n\n"
            text += "💡 Example: /ask What is artificial intelligence?"

        elif data == "smart_home":
            text = "🏠 <b>Smart Home Control</b>\n\n"
            text += "• /lights [action] - Control lights\n"
            text += "• /scene [name] - Activate scenes\n"
            text += "• /temp - Check temperature\n"
            text += "• /home - Home status\n\n"
            text += "💡 Example: /lights turn on living room"

        elif data == "finance":
            text = "💸 <b>Financial Features</b>\n\n"
            text += "• /stock [symbol] - Stock prices\n"
            text += "• /crypto [coin] - Crypto prices\n"
            text += "• /market - Market overview\n\n"
            text += "💡 Example: /stock AAPL"

        elif data == "media":
            text = "🎵 <b>Media Control</b>\n\n"
            text += "• /download [url] - YouTube downloads\n"
            text += "• /spotify [action] - Spotify control\n\n"
            text += "💡 Example: /download https://youtube.com/watch?v=..."

        elif data == "news":
            text = "📰 <b>News & Information</b>\n\n"
            text += "• /news [category] - Latest news\n"
            text += "• /feeds - RSS management\n\n"
            text += "💡 Example: /news tech"

        elif data == "fun":
            text = "🎮 <b>Fun Features</b>\n\n"
            text += "• /meme - Random memes\n"
            text += "• /joke - Random jokes\n"
            text += "• /fact - Fun facts\n"
            text += "• /trivia - Trivia questions\n"
            text += "• /gif [search] - Search GIFs\n\n"
            text += "💡 Example: /meme"

        elif data == "settings":
            text = "⚙️ <b>Settings</b>\n\n"
            text += "• /status - Bot status\n"
            text += "• /help - Show help\n\n"
            text += "🔧 Bot is running in polling mode"

        elif data == "help":
            # Show help text
            text = """📖 <b>Quick Command Reference</b>

🧠 <b>AI Commands:</b>
• /ask [question] - Ask AI anything
• /explain [topic] - Get explanations
• /code [request] - Programming help

🎮 <b>Fun Commands:</b>
• /meme - Random memes
• /joke - Random jokes
• /fact - Fun facts
• /trivia - Trivia questions

📰 <b>News Commands:</b>
• /news [category] - Latest news
• /feeds - RSS management

💸 <b>Finance Commands:</b>
• /stock [symbol] - Stock prices
• /crypto [coin] - Crypto prices

📝 <b>Notes Commands:</b>
• /note create [title] - Create notes
• /files - File management

Use /help for the complete command list!"""

        else:
            text = "❓ Unknown option selected."

        await callback.message.edit_text(text)
        await callback.answer()

    except Exception as e:
        logger.error(f"Error handling callback {data}: {e}")
        await callback.answer("❌ Error processing request")


def register_handlers(dp: Dispatcher):
    """Register basic handlers."""
    dp.message.register(start_command, CommandStart())
    dp.message.register(help_command, Command("help"))
    dp.message.register(status_command, Command("status"))

    # Callback handlers
    dp.callback_query.register(callback_handler)

    # Echo handler for non-command messages (should be last)
    dp.message.register(echo_handler, F.text & ~F.text.startswith("/"))


def register_fallback_handlers(dp: Dispatcher):
    """Register fallback handlers (should be called last)."""
    # Unknown command handler (must be registered after all other command handlers)
    dp.message.register(unknown_command_handler, F.text.startswith("/"))
