"""Benchmark market data routes"""
import logging
import re
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.api.schemas.benchmark import BenchmarkPoint, BenchmarkResponse
from app.services.webull_market_data import WebullMarketDataService

router = APIRouter()
_log = logging.getLogger(__name__)

_TICKER_RE = re.compile(r"^[A-Z0-9\.\-\^]{1,10}$")


@router.get("/{ticker}/performance", response_model=BenchmarkResponse)
def get_benchmark_performance(
    ticker: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> BenchmarkResponse:
    ticker = ticker.upper().strip()
    if not _TICKER_RE.match(ticker):
        raise HTTPException(status_code=422, detail="Invalid ticker symbol")

    try:
        svc = WebullMarketDataService()
        if not svc.app_key or not svc.app_secret:
            return BenchmarkResponse(
                ticker=ticker,
                timeseries=[],
                warning="Webull API credentials not configured — benchmark unavailable",
            )

        bars = svc.get_historical_bars(ticker, timespan="W", count=260)
        if not bars:
            return BenchmarkResponse(
                ticker=ticker,
                timeseries=[],
                warning=f"No data returned from Webull for {ticker}",
            )

        points: list[BenchmarkPoint] = []
        for bar in bars:
            if not isinstance(bar, dict):
                continue
            raw_date = bar.get("date") or bar.get("time") or bar.get("timestamp")
            raw_close = bar.get("close") or bar.get("vwap") or bar.get("open")
            if raw_date is None or raw_close is None:
                continue
            try:
                if isinstance(raw_date, str):
                    bar_date = date.fromisoformat(raw_date[:10])
                else:
                    bar_date = date.fromtimestamp(int(raw_date) / 1000)
                close_val = float(raw_close)
            except (ValueError, TypeError, OSError):
                continue

            if start_date and bar_date < start_date:
                continue
            if end_date and bar_date > end_date:
                continue
            points.append(BenchmarkPoint(date=bar_date, close=close_val))

        # Webull returns most-recent-first; reverse for ascending chronological order
        points.sort(key=lambda p: p.date)

        return BenchmarkResponse(ticker=ticker, timeseries=points)

    except Exception as exc:
        _log.warning("Benchmark fetch failed for %s: %s", ticker, exc)
        return BenchmarkResponse(
            ticker=ticker,
            timeseries=[],
            warning=f"Failed to fetch benchmark data: {exc}",
        )
