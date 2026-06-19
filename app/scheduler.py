import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_scheduler: AsyncIOScheduler = None


async def _run_daily_digest():
    """Job function that runs every morning."""
    from app.services.daily_digest import build_and_send_digest
    settings = get_settings()
    logger.info("daily_digest_job_triggered", recipient=settings.digest_recipient)
    try:
        result = await build_and_send_digest(settings.digest_recipient)
        if result["success"]:
            logger.info("daily_digest_job_success", **result)
        else:
            logger.error("daily_digest_job_failed", reason=result.get("reason"))
    except Exception as exc:
        logger.error("daily_digest_job_error", error=str(exc))


def start_scheduler() -> AsyncIOScheduler:
    """Start the APScheduler with the daily digest job."""
    global _scheduler
    settings = get_settings()

    _scheduler = AsyncIOScheduler(timezone=settings.digest_timezone)

    # Parse hour and minute from digest_time (e.g. "07:00")
    hour, minute = settings.digest_time.split(":")

    _scheduler.add_job(
        _run_daily_digest,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        id="daily_news_digest",
        name="Daily Morning AI News Digest",
        replace_existing=True,
        misfire_grace_time=300,  # 5 min grace if server was briefly down
    )

    _scheduler.start()

    next_run = _scheduler.get_job("daily_news_digest").next_run_time
    logger.info(
        "scheduler_started",
        job="daily_news_digest",
        time=settings.digest_time,
        timezone=settings.digest_timezone,
        recipient=settings.digest_recipient,
        next_run=str(next_run),
    )
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("scheduler_stopped")


def get_scheduler_status() -> dict:
    global _scheduler
    if not _scheduler:
        return {"running": False}
    job = _scheduler.get_job("daily_news_digest")
    return {
        "running": _scheduler.running,
        "job_id": "daily_news_digest",
        "next_run": str(job.next_run_time) if job else None,
        "timezone": str(_scheduler.timezone),
    }
