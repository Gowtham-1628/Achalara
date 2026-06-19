"""Trade validation and ingestion service"""
from typing import List, Tuple, Dict
from datetime import datetime
from pydantic import BaseModel, ValidationError, field_validator
from enum import Enum
import logging


class TradeAction(str, Enum):
    """Trade action type"""

    BUY = "BUY"
    SELL = "SELL"


class TradeDataModel(BaseModel):
    """Trade data validation model"""

    trade_date: str
    symbol: str
    action: TradeAction
    quantity: float
    price: float
    commission: float = 0.0
    strategy: str
    account: str = ""
    notes: str = ""

    @field_validator("quantity", "price")
    @classmethod
    def positive_numbers(cls, v):
        if v <= 0:
            raise ValueError("Must be positive")
        return v

    @field_validator("commission")
    @classmethod
    def non_negative_commission(cls, v):
        if v < 0:
            raise ValueError("Must be non-negative")
        return v

    @field_validator("trade_date")
    @classmethod
    def valid_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


class TradeValidator:
    """Validates and ingests trades from external sources"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.errors = []
        self.warnings = []

    def validate_row(
        self, row: Dict, row_number: int
    ) -> Tuple[bool, TradeDataModel | None]:
        """Validate a single trade row"""
        try:
            cleaned_row = self._clean_row(row)
            trade = TradeDataModel(**cleaned_row)
            return True, trade
        except ValidationError as e:
            error_msg = f"Row {row_number}: {e.errors()[0]['msg']}"
            self.errors.append(error_msg)
            self.logger.error(error_msg)
            return False, None
        except Exception as e:
            error_msg = f"Row {row_number}: {str(e)}"
            self.errors.append(error_msg)
            self.logger.error(error_msg)
            return False, None

    def _clean_row(self, row: Dict) -> Dict:
        """Clean and normalize row data"""
        # Convert date format from YYYY/MM/DD to YYYY-MM-DD if needed
        date_str = str(row.get("Date", "") or "").strip()
        if "/" in date_str:
            # Convert YYYY/MM/DD to YYYY-MM-DD
            date_str = date_str.replace("/", "-")

        return {
            "trade_date": date_str,
            "symbol": str(row.get("Symbol", "") or "").strip().upper(),
            "action": str(row.get("Action", "") or "").strip().upper(),
            "quantity": float(row.get("Quantity") or 0),
            "price": float(row.get("Price") or 0),
            "commission": float(row.get("Commission") or 0),
            "strategy": str(row.get("Strategy", "") or "").strip(),
            "account": str(row.get("Account", "") or "").strip(),
            "notes": str(row.get("Notes", "") or "").strip(),
        }

    def validate_batch(self, rows: List[Dict]) -> Dict:
        """Validate multiple rows"""
        self.errors = []  # Reset errors
        valid_trades = []
        invalid_count = 0

        for idx, row in enumerate(rows, start=2):  # Start at 2 (skip header)
            is_valid, trade = self.validate_row(row, idx)
            if is_valid:
                valid_trades.append(trade)
            else:
                invalid_count += 1

        return {
            "total": len(rows),
            "valid": len(valid_trades),
            "invalid": invalid_count,
            "trades": valid_trades,
            "errors": self.errors,
        }

    def detect_duplicates(
        self, trades: List[TradeDataModel], existing_trades: List
    ) -> List[int]:
        """Detect duplicate trades

        Compares new trades with existing trades in database.
        TradeDataModel has string dates and float amounts,
        Trade objects have date objects and Decimal amounts.
        """
        from datetime import datetime

        duplicates = []
        for idx, trade in enumerate(trades):
            # Convert trade_date string to date for comparison
            try:
                trade_date = datetime.strptime(trade.trade_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue

            for existing in existing_trades:
                # Compare with type conversions
                if (
                    trade_date == existing.trade_date
                    and trade.symbol.upper() == existing.symbol.upper()
                    and float(existing.quantity) == trade.quantity
                    and float(existing.price) == trade.price
                ):
                    duplicates.append(idx)
                    break

        return duplicates
