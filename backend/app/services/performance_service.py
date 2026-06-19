"""Performance orchestration across sleeve / account / client levels.

Computes a summary (MWR, TWR, total return, cost basis, market value) plus a
chart-ready value time-series for an arbitrary set of sleeves. Passing a single
sleeve gives a sleeve-level view; all of an account's sleeves give the account
roll-up; all of a client's sleeves give the client roll-up. Aggregate returns are
computed on the *merged* underlying cash-flow streams, not by averaging child
returns.
"""
import calendar
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.position import Position
from app.models.sleeve import Sleeve
from app.models.trade import Trade
from app.services.mwr_calculation import MWRCalculationService
from app.services.twr_calculation import TWRCalculationService
from app.services.portfolio_calculation import PortfolioCalculationService
from app.services.webull_market_data import WebullMarketDataService


class PerformanceService:
    """Builds multi-level performance payloads from sleeve sets."""

    def __init__(self, db: Session):
        self.db = db
        self.mwr = MWRCalculationService(db)
        self.twr = TWRCalculationService(db)
        self.portfolio = PortfolioCalculationService(db)

    # -- sleeve-set resolution ------------------------------------------------

    def sleeve_ids_for_account(self, account_id: str) -> List[str]:
        rows = self.db.query(Sleeve.id).filter(Sleeve.account_id == account_id).all()
        return [r[0] for r in rows]

    def sleeve_ids_for_client(self, client_id: str) -> List[str]:
        rows = (
            self.db.query(Sleeve.id)
            .join(Account, Sleeve.account_id == Account.id)
            .filter(Account.client_id == client_id)
            .all()
        )
        return [r[0] for r in rows]

    # -- core -----------------------------------------------------------------

    def _fetch_live_prices(self, sleeve_ids: List[str]) -> Dict[str, Decimal]:
        """Fetch live prices from Webull for open positions, persist them, and return.

        Falls back to the last persisted current_price for any symbol that fails
        or when Webull credentials are not configured.
        """
        open_positions = (
            self.db.query(Position)
            .filter(Position.sleeve_id.in_(sleeve_ids), Position.status == "OPEN")
            .all()
        )
        if not open_positions:
            return {}

        # Seed with persisted prices so closed positions still have values.
        prices: Dict[str, Decimal] = {}
        for p in open_positions:
            if p.current_price is not None:
                prices[p.symbol] = p.current_price

        webull = WebullMarketDataService()
        if not webull.app_key or not webull.app_secret:
            return prices

        for pos in open_positions:
            try:
                live = webull.get_current_price(pos.symbol)
                if live is not None:
                    prices[pos.symbol] = Decimal(str(live))
                    pos.current_price = Decimal(str(live))
            except Exception:
                pass  # keep persisted price

        try:
            self.db.commit()
        except Exception:
            self.db.rollback()

        return prices

    def performance(
        self,
        sleeve_ids: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        prices: Optional[Dict[str, Decimal]] = None,
    ) -> Dict:
        """Summary metrics + value time-series for a set of sleeves.

        Returns an empty/zeroed payload when the sleeve set has no trades.
        """
        sleeve_ids = list(sleeve_ids)
        if prices is None:
            prices = self._fetch_live_prices(sleeve_ids) if sleeve_ids else {}

        trades = (
            self.db.query(Trade).filter(Trade.sleeve_id.in_(sleeve_ids)).all()
            if sleeve_ids
            else []
        )

        if not trades:
            return {
                "summary": {
                    "mwr_pct": None,
                    "twr_pct": None,
                    "total_return_pct": None,
                    "total_cost_basis": 0.0,
                    "total_market_value": 0.0,
                    "total_unrealized_gain": 0.0,
                    "trades_count": 0,
                },
                "timeseries": [],
            }

        s_start = start_date or min(t.trade_date for t in trades)
        s_end = end_date or max(t.trade_date for t in trades)

        try:
            mwr = self.mwr.calculate_mwr(sleeve_ids, s_start, s_end)
        except Exception:
            mwr = None
        try:
            twr = self.twr.calculate_twr(sleeve_ids, s_start, s_end)
        except Exception:
            twr = None

        valued = self.portfolio.calculate_account_value(sleeve_ids, prices)
        timeseries = self.portfolio.value_series(sleeve_ids, prices)

        # Closed-position roll-ups
        closed = valued.get("closed_positions", [])
        total_invested = sum(
            float(p.get("matched_quantity", 0)) * float(p.get("entry_price", 0))
            for p in closed
        )
        total_proceeds = sum(
            float(p.get("matched_quantity", 0)) * float(p.get("exit_price", 0))
            for p in closed
        )
        total_realized_gain = valued.get("total_realized_gain", 0.0)

        twr_note = (
            "N/A — TWR requires open positions to mark to market; "
            "all positions are closed (round-trip portfolio)"
            if twr is None
            else None
        )

        return {
            "summary": {
                "mwr_pct": float(mwr) if mwr is not None else None,
                "twr_pct": float(twr) if twr is not None else None,
                "twr_note": twr_note,
                "total_return_pct": valued.get("total_return_pct"),
                "total_cost_basis": valued.get("total_cost_basis", 0.0),
                "total_market_value": valued.get("total_market_value", 0.0),
                "total_unrealized_gain": valued.get("total_unrealized_gain", 0.0),
                "total_invested": total_invested,
                "total_proceeds": total_proceeds,
                "total_realized_gain": total_realized_gain,
                "closed_positions_count": valued.get("closed_positions_count", 0),
                "trades_count": len(trades),
            },
            "start_date": s_start,
            "end_date": s_end,
            "timeseries": timeseries,
        }

    def monthly_returns(self, sleeve_ids: List[str]) -> List[Dict]:
        """Month-on-month return breakdown since inception.

        For each calendar month:
          - start_value: portfolio value at the last trade date of the prior month
            (0 for the inception month)
          - end_value:   portfolio value at the last trade date within the month,
            or at end-of-month if no trade fell in that month
          - cash_in / cash_out: gross BUY / SELL amounts during the month
          - realized_gain: net realized P&L from SELLs closed in the month
          - return_pct: (end_value + cash_out - cash_in - start_value) / start_value
            (modified Dietz approximation); None for the inception month

        Open positions are valued at live prices fetched in _fetch_live_prices.
        """
        sleeve_ids = list(sleeve_ids)
        prices = self._fetch_live_prices(sleeve_ids)

        trades = (
            self.db.query(Trade)
            .filter(Trade.sleeve_id.in_(sleeve_ids))
            .order_by(Trade.trade_date)
            .all()
        )
        if not trades:
            return []

        first_date = min(t.trade_date for t in trades)
        last_date = max(t.trade_date for t in trades)

        # Build a lookup: date → portfolio value from value_series
        series = self.portfolio.value_series(sleeve_ids, prices)
        value_by_date: Dict[date, float] = {pt["date"]: pt["value"] for pt in series}

        def value_at_or_before(d: date) -> float:
            """Latest portfolio value on or before date d."""
            candidates = [v for dt, v in value_by_date.items() if dt <= d]
            return candidates[-1] if candidates else 0.0

        # Enumerate calendar months from inception to last trade month
        months = []
        year, month = first_date.year, first_date.month
        end_year, end_month = last_date.year, last_date.month

        prev_end_value = 0.0  # value carried from previous month

        while (year, month) <= (end_year, end_month):
            month_last_day = calendar.monthrange(year, month)[1]
            month_start = date(year, month, 1)
            month_end = date(year, month, month_last_day)

            # Clamp to the actual data range
            effective_end = min(month_end, last_date)

            end_value = value_at_or_before(effective_end)

            # Cash flows within this month
            month_trades = [
                t for t in trades
                if date(year, month, 1) <= t.trade_date <= effective_end
            ]
            cash_in = sum(
                float(t.quantity) * float(t.price) + float(t.commission)
                for t in month_trades if t.action == "BUY"
            )
            cash_out = sum(
                float(t.quantity) * float(t.price) - float(t.commission)
                for t in month_trades if t.action == "SELL"
            )

            # Realized gain: SELL proceeds minus matched BUY cost for pairs closed this month
            closed_result = self.portfolio.calculate_positions(
                sleeve_ids, as_of_date=effective_end
            )
            realized_this_month = sum(
                float(p["realized_gain"])
                for p in closed_result["closed"]
                if p["closed_at"] and date(year, month, 1) <= p["closed_at"] <= effective_end
            )

            # Modified Dietz return: None for inception month (no prior value)
            is_inception = (year == first_date.year and month == first_date.month)
            if is_inception or prev_end_value == 0:
                return_pct = None
            else:
                # return = (end - start - net_cash_in) / start
                net_invested = cash_in - cash_out
                denom = prev_end_value
                return_pct = ((end_value - prev_end_value - net_invested) / denom * 100) if denom else None

            month_label = date(year, month, 1).strftime("%b %Y")
            months.append({
                "year": year,
                "month": month,
                "month_label": month_label,
                "start_value": prev_end_value,
                "end_value": end_value,
                "cash_in": cash_in,
                "cash_out": cash_out,
                "net_cash_flow": cash_in - cash_out,
                "realized_gain": realized_this_month,
                "return_pct": round(return_pct, 2) if return_pct is not None else None,
            })

            prev_end_value = end_value

            # Advance to next month
            if month == 12:
                year, month = year + 1, 1
            else:
                month += 1

        return months
