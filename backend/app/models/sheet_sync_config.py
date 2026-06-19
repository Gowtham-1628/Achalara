"""Sheet sync configuration model"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
import uuid
from app.models.base import BaseModel


class SheetSyncConfig(BaseModel):
    """Maps a Google Sheet range to a sleeve for automated daily sync.

    The client is derived through ``sleeve -> account.client_id``; it is not
    stored here.
    """

    __tablename__ = "sheet_sync_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sleeve_id = Column(
        String(36), ForeignKey("sleeves.id", ondelete="CASCADE"), nullable=False
    )
    sheet_id = Column(String(255), nullable=False)
    range_name = Column(String(100), nullable=False, default="Sheet1")
    enabled = Column(Boolean, nullable=False, default=True)
    last_synced_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<SheetSyncConfig(id={self.id}, sleeve_id={self.sleeve_id}, sheet_id={self.sheet_id})>"
