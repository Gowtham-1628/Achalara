"""Reusable daily sync logic shared by the route handler and the scheduler job."""
import csv
import io
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.services.google_sheets_sync import GoogleSheetsService
from app.services.trade_import import TradeImportService
from app.models.sheet_sync_config import SheetSyncConfig

logger = logging.getLogger(__name__)


def run_daily_sync(
    db: Session,
    sleeve_id: str,
    sheet_id: str,
    range_name: str = "Sheet1",
) -> dict:
    """
    Fetch trades from a Google Sheet and import new ones into the given sleeve.

    Returns the same result dict as TradeImportService.import_from_file, plus
    a top-level 'sheet_rows' key with the raw row count fetched.

    Raises ValueError / ConnectionError so callers can translate to HTTP errors.
    """
    sheets_service = GoogleSheetsService()
    rows = sheets_service.fetch_sheet_data(sheet_id, range_name)

    if not rows:
        return {
            "success": True,
            "total": 0,
            "imported": 0,
            "duplicates": 0,
            "errors": [],
            "sync_log_id": None,
            "sheet_rows": 0,
        }

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    file_content = output.getvalue().encode("utf-8")

    import_service = TradeImportService(db)
    result = import_service.import_from_file(
        file_content, sleeve_id, mode="IMPORT", import_type="DAILY"
    )
    result["sheet_rows"] = len(rows)
    return result


def run_all_enabled_syncs(db: Session) -> None:
    """Called by the APScheduler job — iterates all enabled SheetSyncConfig rows."""
    configs = db.query(SheetSyncConfig).filter(SheetSyncConfig.enabled.is_(True)).all()
    logger.info(f"Daily sync job starting: {len(configs)} config(s) to process")

    for cfg in configs:
        try:
            result = run_daily_sync(
                db=db,
                sleeve_id=cfg.sleeve_id,
                sheet_id=cfg.sheet_id,
                range_name=cfg.range_name,
            )
            cfg.last_synced_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(
                f"Synced config {cfg.id}: imported={result['imported']}, "
                f"duplicates={result['duplicates']}"
            )
        except Exception as exc:
            logger.error(f"Daily sync failed for config {cfg.id}: {exc}")
            db.rollback()
