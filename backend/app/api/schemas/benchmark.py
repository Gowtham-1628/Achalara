"""Benchmark market data response schemas"""
from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class BenchmarkPoint(BaseModel):
    date: date
    close: float


class BenchmarkResponse(BaseModel):
    ticker: str
    timeseries: List[BenchmarkPoint]
    warning: Optional[str] = None
