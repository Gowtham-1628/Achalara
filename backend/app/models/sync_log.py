"""Sync/Import log model"""
from sqlalchemy import Column, String, Integer, JSON, DateTime
import uuid
from app.models.base import BaseModel


class SyncLog(BaseModel):
    """Google Sheets sync/import audit trail"""

    __tablename__ = "sync_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    import_type = Column(String(20), nullable=False)  # HISTORICAL or DAILY
    status = Column(String(20), nullable=False)  # PENDING, SUCCESS, FAILED
    rows_processed = Column(Integer, default=0)
    rows_success = Column(Integer, default=0)
    rows_failed = Column(Integer, default=0)
    error_details = Column(JSON)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<SyncLog(id={self.id}, type={self.import_type}, status={self.status})>"
