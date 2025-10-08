"""Middleware for the bot."""

import logging
import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Dispatcher
from aiogram.types import TelegramObject, User, Message

from bot.config import settings
from bot.utils.metrics import request_counter, request_duration


logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Middleware to check if user is authorized."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user: User = data.get("event_from_user")
        
        if user and settings.allowed_user_ids:
            if user.id not in settings.allowed_user_ids:
                logger.warning(f"Unauthorized access attempt from user {user.id}")
                if isinstance(event, Message):
                    await event.answer("❌ You are not authorized to use this bot.")
                return
        
        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging requests."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        start_time = time.time()
        user: User = data.get("event_from_user")
        
        # Log the request
        if isinstance(event, Message):
            logger.info(
                f"Message from {user.id} (@{user.username}): {event.text[:100]}..."
                if event.text else f"Non-text message from {user.id}"
            )
        
        try:
            result = await handler(event, data)
            
            # Update metrics
            duration = time.time() - start_time
            request_counter.inc()
            request_duration.observe(duration)
            
            return result
            
        except Exception as e:
            logger.error(f"Error handling message from {user.id}: {e}")
            raise


class RateLimitMiddleware(BaseMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, rate_limit: int = 10):
        self.rate_limit = rate_limit
        self.user_requests = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user: User = data.get("event_from_user")
        
        if user:
            current_time = time.time()
            user_id = user.id
            
            # Clean old requests
            if user_id in self.user_requests:
                self.user_requests[user_id] = [
                    req_time for req_time in self.user_requests[user_id]
                    if current_time - req_time < 60  # 1 minute window
                ]
            else:
                self.user_requests[user_id] = []
            
            # Check rate limit
            if len(self.user_requests[user_id]) >= self.rate_limit:
                if isinstance(event, Message):
                    await event.answer("⏰ Rate limit exceeded. Please wait a moment.")
                return
            
            # Add current request
            self.user_requests[user_id].append(current_time)
        
        return await handler(event, data)


def setup_middleware(dp: Dispatcher):
    """Setup all middleware for the dispatcher."""
    # Temporarily disable AuthMiddleware to test - authorization is handled by decorators
    # dp.message.middleware(AuthMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(RateLimitMiddleware())

    logger.info("Middleware setup complete")
