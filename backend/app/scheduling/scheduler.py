"""
Background scheduler for Automata TG.

Uses APScheduler to run periodic tasks:
- Scheduled content generation
- Publishing jobs
- Usage reset (monthly)
"""
from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def _daily_generation_job() -> None:
    """
    Placeholder: Find all active channels that need content today,
    generate posts, and queue them for approval or auto-publish.
    Full implementation added when channel onboarding is complete.
    """
    logger.info("Daily generation job — placeholder (implement when onboarding ready)")


async def _monthly_usage_summary_job() -> None:
    """Monthly: archive usage snapshots if needed."""
    logger.info("Monthly usage summary job — placeholder")


def start_scheduler() -> None:
    scheduler.add_job(
        _daily_generation_job,
        CronTrigger(hour=8, minute=0),
        id="daily_generation",
        replace_existing=True,
    )
    scheduler.add_job(
        _monthly_usage_summary_job,
        CronTrigger(day=1, hour=0, minute=5),
        id="monthly_usage_summary",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started.")


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")
