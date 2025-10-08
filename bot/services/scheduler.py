"""Scheduler service for periodic tasks."""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from bot.config import settings


logger = logging.getLogger(__name__)

# Configure job stores and executors
jobstores = {
    'default': SQLAlchemyJobStore(url=settings.database_url)
}

executors = {
    'default': AsyncIOExecutor()
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

# Create scheduler
scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone='UTC'
)


async def market_open_notification():
    """Send market open notification."""
    logger.info("Market open notification triggered")
    # TODO: Implement market open notification


async def daily_portfolio_update():
    """Send daily portfolio update."""
    logger.info("Daily portfolio update triggered")
    # TODO: Implement portfolio update


async def news_digest():
    """Send daily news digest."""
    logger.info("News digest triggered")
    # TODO: Implement news digest


async def backup_data():
    """Backup important data."""
    logger.info("Data backup triggered")
    # TODO: Implement data backup


def setup_scheduled_jobs():
    """Setup all scheduled jobs."""
    
    # Market notifications (weekdays at 9:30 AM EST)
    scheduler.add_job(
        market_open_notification,
        'cron',
        day_of_week='mon-fri',
        hour=14,  # 9:30 AM EST = 2:30 PM UTC
        minute=30,
        id='market_open'
    )
    
    # Daily portfolio update (weekdays at 6 PM EST)
    scheduler.add_job(
        daily_portfolio_update,
        'cron',
        day_of_week='mon-fri',
        hour=23,  # 6 PM EST = 11 PM UTC
        minute=0,
        id='portfolio_update'
    )
    
    # Daily news digest (every day at 8 AM)
    scheduler.add_job(
        news_digest,
        'cron',
        hour=8,
        minute=0,
        id='news_digest'
    )
    
    # Weekly data backup (Sundays at 2 AM)
    scheduler.add_job(
        backup_data,
        'cron',
        day_of_week='sun',
        hour=2,
        minute=0,
        id='data_backup'
    )
    
    logger.info("Scheduled jobs configured")


# Setup jobs when module is imported
setup_scheduled_jobs()
