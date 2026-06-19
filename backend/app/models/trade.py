"""Trade model"""
from sqlalchemy import Column, String, Numeric, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
import uuid
from app.models.base import BaseModel


class Trade(BaseModel):
    """Individual trade transaction"""

    __tablename__ = "trades"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sleeve_id = Column(
        String(36), ForeignKey("sleeves.id", ondelete="CASCADE"), nullable=False
    )
    trade_date = Column(Date, nullable=False)
    symbol = Column(String(20), nullable=False)
    action = Column(String(10), nullable=False)  # BUY or SELL
    quantity = Column(Numeric(15, 6), nullable=False)
    price = Column(Numeric(15, 6), nullable=False)
    commission = Column(Numeric(15, 6), default=0)
    notes = Column(String(500))
    google_sheet_row_id = Column(String(255), unique=True)

    __table_args__ = (
        CheckConstraint("action IN ('BUY', 'SELL')", name="valid_action"),
        CheckConstraint("quantity > 0", name="positive_quantity"),
        CheckConstraint("price > 0", name="positive_price"),
    )

    sleeve = relationship("Sleeve", back_populates="trades")

    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, action={self.action}, qty={self.quantity})>"
