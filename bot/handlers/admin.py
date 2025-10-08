"""Admin command handlers."""

import logging
import psutil
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

from bot.utils.decorators import admin_only, log_command
from bot.utils.metrics import generate_metrics


logger = logging.getLogger(__name__)


@admin_only
@log_command
async def logs_command(message: Message):
    """Handle /logs command for viewing logs."""
    try:
        with open("logs/bot.log", "r") as f:
            logs = f.readlines()[-20:]  # Last 20 lines
        
        log_text = "📋 <b>Recent Logs:</b>\n\n<code>" + "".join(logs) + "</code>"
        await message.answer(log_text[:4000])  # Telegram message limit
        
    except Exception as e:
        await message.answer(f"❌ Error reading logs: {e}")


@admin_only
@log_command
async def metrics_command(message: Message):
    """Handle /metrics command for performance metrics."""
    try:
        metrics_data = generate_metrics()
        
        # Parse some basic metrics for display
        lines = metrics_data.decode().split('\n')
        important_metrics = [line for line in lines if not line.startswith('#') and line.strip()]
        
        metrics_text = "📊 <b>Bot Metrics:</b>\n\n<code>" + "\n".join(important_metrics[:20]) + "</code>"
        await message.answer(metrics_text)
        
    except Exception as e:
        await message.answer(f"❌ Error getting metrics: {e}")


@admin_only
@log_command
async def restart_command(message: Message):
    """Handle /restart command for restarting services."""
    await message.answer("🔄 Restart functionality coming soon!")


def register_handlers(dp: Dispatcher):
    """Register admin handlers."""
    dp.message.register(logs_command, Command("logs"))
    dp.message.register(metrics_command, Command("metrics"))
    dp.message.register(restart_command, Command("restart"))
