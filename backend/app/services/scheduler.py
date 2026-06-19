"""APScheduler background job that runs the daily Google Sheets sync."""
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db.database import SessionLocal
from app.services.daily_sync import run_all_enabled_syncs

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _job_wrapper() -> None:
    """Open a DB session, run syncs, close session."""
    db = SessionLocal()
    try:
        run_all_enabled_syncs(db)
    except Exception as exc:
        logger.error(f"Unhandled error in daily sync job: {exc}")
    finally:
        db.close()


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler()
    # Run at 4 PM UTC daily (matches ROADMAP default)
    _scheduler.add_job(
        _job_wrapper,
        CronTrigger(hour=16, minute=0),
        id="daily_sheets_sync",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("APScheduler started — daily sync job scheduled at 16:00 UTC")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("APScheduler stopped")


def get_scheduler() -> BackgroundScheduler | None:
    return _scheduler
