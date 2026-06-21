"""Tests for the Money Weighted Return (IRR) calculation service.

These exercise MWRCalculationService directly against the DB session so we can
assert on the numeric IRR rather than the rolled-up API response. Trades are
created through the API (which shares the same session as the `db` fixture via
the dependency override in conftest) to keep model/constraint handling honest.
"""
from datetime import date

import pytest

from app.services.mwr_calculation import MWRCalculationService
from tests.conftest import create_test_strategy


def _add_trade(client, sleeve_id, trade_date, action, quantity, price, commission=0.0):
    resp = client.post(
        "/api/v1/trades/",
        json={
            "sleeve_id": sleeve_id,
            "trade_date": trade_date,
            "symbol": "AAPL",
            "action": action,
            "quantity": quantity,
            "price": price,
            "commission": commission,
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


class TestMWRCalculation:
    def test_single_round_trip_positive_return(self, client, db):
        """Buy 100@100, sell 100@110 a year later → ~10% holding-period return."""
        _, _, sleeve_id = create_test_strategy(
            client, client_email="mwr1@test.com", strategy_name="MWR RT"
        )
        _add_trade(client, sleeve_id, "2024-01-01", "BUY", 100, 100.0)
        _add_trade(client, sleeve_id, "2024-12-31", "SELL", 100, 110.0)

        svc = MWRCalculationService(db)
        mwr = svc.calculate_mwr([sleeve_id], date(2024, 1, 1), date(2024, 12, 31))

        # Outflow 10,000 → inflow 11,000 over ~1y. HPR ≈ 0.10.
        assert mwr == pytest.approx(0.10, abs=0.005)

    def test_loss_round_trip_negative_return(self, client, db):
        """Buy high, sell low → negative MWR."""
        _, _, sleeve_id = create_test_strategy(
            client, client_email="mwr_loss@test.com", strategy_name="MWR Loss"
        )
        _add_trade(client, sleeve_id, "2024-01-01", "BUY", 100, 100.0)
        _add_trade(client, sleeve_id, "2024-12-31", "SELL", 100, 90.0)

        svc = MWRCalculationService(db)
        mwr = svc.calculate_mwr([sleeve_id], date(2024, 1, 1), date(2024, 12, 31))

        assert mwr < 0
        assert mwr == pytest.approx(-0.10, abs=0.005)

    def test_multiple_buys_partial_sell_open_position(self, client, db):
        """Two buys at different prices, partial sell — open position carried.

        The remaining open shares are valued at the last-trade price as a
        terminal inflow, so MWR should be well-defined and finite.
        """
        _, _, sleeve_id = create_test_strategy(
            client, client_email="mwr_multi@test.com", strategy_name="MWR Multi"
        )
        _add_trade(client, sleeve_id, "2024-01-01", "BUY", 100, 100.0)
        _add_trade(client, sleeve_id, "2024-06-01", "BUY", 100, 120.0)
        _add_trade(client, sleeve_id, "2024-12-01", "SELL", 50, 130.0)

        svc = MWRCalculationService(db)
        mwr = svc.calculate_mwr([sleeve_id], date(2024, 1, 1), date(2024, 12, 1))

        # 150 shares remain open at the last trade price (130). Net the portfolio
        # appreciated, so MWR should be positive and finite.
        assert mwr > 0
        assert mwr < 5.0  # sanity: not a runaway value

    def test_same_day_start_end_returns_zero(self, client, db):
        """start_date == end_date → no elapsed time → 0.0 (inception-week regression guard)."""
        _, _, sleeve_id = create_test_strategy(
            client, client_email="mwr_sameday@test.com", strategy_name="MWR SameDay"
        )
        _add_trade(client, sleeve_id, "2024-03-18", "BUY", 100, 100.0)

        svc = MWRCalculationService(db)
        mwr = svc.calculate_mwr([sleeve_id], date(2024, 3, 18), date(2024, 3, 18))

        assert mwr == 0.0

    def test_fully_closed_portfolio_cash_flow_only(self, client, db):
        """All positions closed → closing value 0; IRR solved from BUY/SELL stream."""
        _, _, sleeve_id = create_test_strategy(
            client, client_email="mwr_closed@test.com", strategy_name="MWR Closed"
        )
        _add_trade(client, sleeve_id, "2024-01-01", "BUY", 100, 50.0)
        _add_trade(client, sleeve_id, "2024-07-01", "SELL", 100, 60.0)

        svc = MWRCalculationService(db)
        mwr = svc.calculate_mwr([sleeve_id], date(2024, 1, 1), date(2024, 7, 1))

        # 5,000 out → 6,000 in over half a year. Positive, finite.
        assert mwr > 0
        assert mwr < 1.0

    def test_no_trades_returns_zero(self, client, db):
        """No trades in the window → 0.0, not an error."""
        _, _, sleeve_id = create_test_strategy(
            client, client_email="mwr_empty@test.com", strategy_name="MWR Empty"
        )

        svc = MWRCalculationService(db)
        mwr = svc.calculate_mwr([sleeve_id], date(2024, 1, 1), date(2024, 12, 31))

        assert mwr == 0.0
