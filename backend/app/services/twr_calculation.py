"""Time Weighted Return (TWR) calculation service"""
from decimal import Decimal
from datetime import date
from typing import List
import logging

from app.models.trade import Trade
from app.models.position import Position
from app.services.portfolio_calculation import _as_sleeve_ids


class TWRCalculationService:
    """Service for calculating Time Weighted Return.

    For a round-trip trading portfolio (all positions closed), TWR is computed
    by treating each closed round-trip as a sub-period:

        holding_period_return_i = (exit_price - entry_price) / entry_price

    and geometrically linking them:

        TWR = Product(1 + hpr_i) - 1

    This eliminates the distortion caused by external cash flows (new BUYs) and
    correctly reflects the manager's compounded stock-selection skill across all
    round-trips. For portfolios with open positions at end_date, those are
    valued at last-trade price and added as an additional sub-period return.
    """

    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def calculate_twr(self, sleeve_ids, start_date: date, end_date: date):
        """
        Calculate Time Weighted Return.

        TWR requires marking open positions to market at each sub-period
        boundary. For a fully-closed portfolio (all positions are round-trips
        with no open holdings at end_date) there is nothing to mark to market,
        so TWR is not applicable and None is returned. A mixed portfolio (some
        open positions) returns a valid TWR using last-trade price as the
        market-price proxy for open holdings.

        Returns TWR as a decimal (e.g. 0.10 for 10%), or None when N/A.
        """
        from app.services.portfolio_calculation import PortfolioCalculationService

        sleeve_ids = _as_sleeve_ids(sleeve_ids)
        try:
            calc = PortfolioCalculationService(self.db)
            result = calc.calculate_positions(sleeve_ids, as_of_date=end_date)

            # TWR is only meaningful when there are open positions to mark to market.
            if not result["open"]:
                return None

            # Build a symbol→current_price map from persisted Position rows first.
            # Falls back to last-trade price when no live price has been stored.
            persisted: dict = {}
            for row in (
                self.db.query(Position)
                .filter(
                    Position.sleeve_id.in_(sleeve_ids),
                    Position.status == "OPEN",
                    Position.current_price.isnot(None),
                )
                .all()
            ):
                persisted[row.symbol] = Decimal(str(row.current_price))

            period_returns: List[float] = []

            for pos in result["open"]:
                symbol = pos["symbol"]
                cost_basis = Decimal(str(pos["cost_basis"]))
                qty = Decimal(str(pos["quantity"]))
                if qty <= 0 or cost_basis <= 0:
                    continue
                avg_cost = cost_basis / qty

                if symbol in persisted:
                    market_price = persisted[symbol]
                else:
                    last_trade = (
                        self.db.query(Trade)
                        .filter(
                            Trade.sleeve_id.in_(sleeve_ids),
                            Trade.symbol == symbol,
                            Trade.trade_date <= end_date,
                        )
                        .order_by(Trade.trade_date.desc())
                        .first()
                    )
                    if last_trade is None:
                        continue
                    market_price = Decimal(str(last_trade.price))

                hpr = float((market_price - avg_cost) / avg_cost)
                period_returns.append(1.0 + hpr)

            if not period_returns:
                return None

            twr = 1.0
            for r in period_returns:
                twr *= r

            return twr - 1.0

        except Exception as e:
            self.logger.error(f"TWR calculation failed: {e}")
            return None
