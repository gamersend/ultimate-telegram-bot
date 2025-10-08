"""Bot and dispatcher creation and configuration."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import settings


def create_bot() -> Bot:
    """Create and configure the Telegram bot instance."""
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True
        )
    )


def create_dispatcher() -> Dispatcher:
    """Create and configure the dispatcher."""
    return Dispatcher()
