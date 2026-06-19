"""Trade schemas"""
from pydantic import BaseModel, Field
from uuid import UUID  # noqa: F401
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class TradeAction(str, Enum):
    """Trade action type"""

    BUY = "BUY"
    SELL = "SELL"


class TradeCreate(BaseModel):
    """Create trade request"""

    sleeve_id: str  # UUID as string
    trade_date: date
    symbol: str
    action: TradeAction
    quantity: Decimal = Field(gt=0)
    price: Decimal = Field(gt=0)
    commission: Decimal = Field(default=0, ge=0)
    notes: str = ""


class TradeResponse(BaseModel):
    """Trade response"""

    id: str  # UUID as string
    sleeve_id: str
    trade_date: date
    symbol: str
    action: TradeAction
    quantity: Decimal
    price: Decimal
    commission: Decimal
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True
