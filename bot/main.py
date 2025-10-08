"""Main entry point for the Ultimate Telegram Bot."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.config import settings
from bot.core.bot import create_bot, create_dispatcher
from bot.core.database import init_database
from bot.core.logging import setup_logging
from bot.core.middleware import setup_middleware
from bot.handlers import register_handlers
from bot.services.scheduler import scheduler
from bot.utils.metrics import setup_metrics


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Ultimate Telegram Bot...")
    
    # Initialize database
    await init_database()
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started")
    
    # Setup metrics
    setup_metrics()
    logger.info("Metrics initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ultimate Telegram Bot...")
    scheduler.shutdown()
    logger.info("Scheduler stopped")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Ultimate Telegram Bot",
        description="Your all-in-one personal assistant",
        version="1.0.0",
        lifespan=lifespan
    )
    
    return app


async def main():
    """Main application entry point."""
    # Setup logging
    setup_logging()
    
    logger.info("Initializing Ultimate Telegram Bot...")
    
    # Create bot and dispatcher
    bot = create_bot()
    dp = create_dispatcher()
    
    # Setup middleware
    setup_middleware(dp)
    
    # Register handlers
    register_handlers(dp)
    
    # Create FastAPI app
    app = create_app()
    
    if settings.telegram_webhook_url:
        # Webhook mode
        logger.info("Starting in webhook mode...")
        
        # Set webhook
        await bot.set_webhook(
            url=settings.telegram_webhook_url,
            secret_token=settings.telegram_webhook_secret
        )
        
        # Setup webhook handler
        webhook_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=settings.telegram_webhook_secret
        )
        webhook_handler.register(app, path="/webhook")
        
        # Add health check
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "mode": "webhook"}
        
        # Add metrics endpoint
        @app.get("/metrics")
        async def metrics():
            from bot.utils.metrics import generate_metrics
            return generate_metrics()
        
        # Start FastAPI server
        config = uvicorn.Config(
            app=app,
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.lower()
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    else:
        # Polling mode
        logger.info("Starting in polling mode...")
        
        # Delete webhook
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Start polling
        await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
