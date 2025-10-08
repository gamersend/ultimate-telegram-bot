"""Handler registration for the bot."""

import logging
from aiogram import Dispatcher

from bot.handlers import (
    basic,
    ai,
    voice,
    image,
    smart_home,
    tesla,
    finance,
    media,
    news,
    notes,
    fun,
    admin
)


logger = logging.getLogger(__name__)


def register_handlers(dp: Dispatcher):
    """Register all handlers with the dispatcher."""

    # Register specific command handlers first
    admin.register_handlers(dp)
    ai.register_handlers(dp)
    voice.register_handlers(dp)
    image.register_handlers(dp)
    smart_home.register_handlers(dp)
    tesla.register_handlers(dp)
    finance.register_handlers(dp)
    media.register_handlers(dp)
    news.register_handlers(dp)
    notes.register_handlers(dp)
    fun.register_handlers(dp)

    # Register basic handlers (including callbacks)
    basic.register_handlers(dp)

    # Register fallback handlers last
    basic.register_fallback_handlers(dp)

    logger.info("All handlers registered successfully")
