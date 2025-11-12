"""Decorators for bot handlers."""

import functools
import logging
from typing import Callable

from aiogram.types import Message

from bot.config import settings


logger = logging.getLogger(__name__)


def authorized_only(func: Callable) -> Callable:
    """Decorator to check if user is authorized."""

    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        logger.info(f"Authorization check for user {user_id}, allowed: {settings.allowed_user_ids}")

        if settings.allowed_user_ids and user_id not in settings.allowed_user_ids:
            logger.warning(f"Unauthorized access attempt from user {user_id}")
            await message.answer("❌ You are not authorized to use this bot.")
            return

        logger.info(f"User {user_id} authorized, executing {func.__name__}")
        return await func(message, *args, **kwargs)

    return wrapper


def admin_only(func: Callable) -> Callable:
    """Decorator for admin-only commands."""

    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        # For now, admin is the first user in allowed_user_ids
        if not settings.allowed_user_ids:
            logger.warning("No admin users configured in allowed_user_ids")
            await message.answer("❌ Admin access is not configured.")
            return

        admin_id = settings.allowed_user_ids[0]

        if message.from_user.id != admin_id:
            await message.answer("❌ This command is only available to administrators.")
            return

        return await func(message, *args, **kwargs)

    return wrapper


def log_command(func: Callable) -> Callable:
    """Decorator to log command usage."""
    
    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        logger.info(
            f"Command {func.__name__} executed by user {message.from_user.id} "
            f"(@{message.from_user.username})"
        )
        
        try:
            return await func(message, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in command {func.__name__}: {e}")
            await message.answer("❌ An error occurred while processing your request.")
            raise
    
    return wrapper
