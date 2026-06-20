"""Client endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from typing import Optional

from app.db.database import get_db
from app.models.client import Client
from app.models.account import Account
from app.models.position import Position
from app.models.sleeve import Sleeve
from app.models.trade import Trade
from app.api.schemas.client import ClientCreate, ClientResponse, ClientLogin
from app.config import settings
from app.api.schemas.performance import LevelPerformance, MonthlyReturnsResponse, MonthlyReturn
from app.services.performance_service import PerformanceService
from app.services.portfolio_calculation import PortfolioCalculationService

router = APIRouter()


@router.post("/", response_model=ClientResponse, status_code=201)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Create a new client"""
    existing = db.query(Client).filter(Client.email == client.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_client = Client(name=client.name, email=client.email)
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.get("/lookup", response_model=ClientResponse)
def lookup_client_by_email(email: str = Query(..., description="Client email address"), db: Session = Depends(get_db)):
    """Look up a client by email address"""
    client = db.query(Client).filter(Client.email == email).first()
    if not client:
        raise HTTPException(status_code=404, detail="No client found with that email")
    return client


@router.post("/login", response_model=ClientResponse)
def login_client(body: ClientLogin, db: Session = Depends(get_db)):
    """Identify a client by email + dev password. Returns client data on success."""
    if body.password != settings.client_dev_password:
        raise HTTPException(status_code=401, detail="Incorrect password")
    client = db.query(Client).filter(Client.email == body.email).first()
    if not client:
        raise HTTPException(status_code=404, detail="No client found with that email")
    return client


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(client_id: str, db: Session = Depends(get_db)):
    """Get client by ID"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("/{client_id}/performance", response_model=LevelPerformance)
def get_client_performance(
    client_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Client-level roll-up of MWR/TWR computed on the merged cash-flow stream
    across every sleeve in the client, plus per-account children."""
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400, detail="start_date must be before end_date"
        )
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    svc = PerformanceService(db)
    all_sleeve_ids = svc.sleeve_ids_for_client(client_id)

    perf = svc.performance(all_sleeve_ids, start_date, end_date)

    accounts = db.query(Account).filter(Account.client_id == client_id).all()
    children = []
    for account in accounts:
        acct_sleeve_ids = svc.sleeve_ids_for_account(account.id)
        child = svc.performance(acct_sleeve_ids, start_date, end_date)
        children.append(
            {
                "level": "account",
                "id": account.id,
                "name": account.name,
                "summary": child["summary"],
            }
        )

    return {
        "level": "client",
        "id": client_id,
        "name": client.name,
        "start_date": perf.get("start_date"),
        "end_date": perf.get("end_date"),
        "summary": perf["summary"],
        "timeseries": perf["timeseries"],
        "children": children,
    }


@router.get("/{client_id}/performance/returns-series")
def get_client_returns_series(
    client_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Weekly TWR + MWR timeseries for a client (aggregated from sleeve snapshots)."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    from app.services.weekly_snapshot_service import WeeklySnapshotService
    svc = PerformanceService(db)
    sleeve_ids = svc.sleeve_ids_for_client(client_id)
    series = WeeklySnapshotService(db).returns_series(sleeve_ids, start_date, end_date)
    return {"level": "client", "id": client_id, "series": series}


@router.get("/{client_id}/performance/monthly", response_model=MonthlyReturnsResponse)
def get_client_monthly_returns(
    client_id: str,
    db: Session = Depends(get_db),
):
    """Month-on-month return breakdown since inception for a client."""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    svc = PerformanceService(db)
    sleeve_ids = svc.sleeve_ids_for_client(client_id)
    months = svc.monthly_returns(sleeve_ids)
    cumulative = None
    non_none = [m["return_pct"] for m in months if m["return_pct"] is not None]
    if non_none:
        product = 1.0
        for r in non_none:
            product *= 1 + r / 100
        cumulative = round((product - 1) * 100, 2)
    return MonthlyReturnsResponse(
        months=[MonthlyReturn(**m) for m in months],
        cumulative_return_pct=cumulative,
    )


@router.get("/{client_id}/positions")
def get_client_positions(client_id: str, db: Session = Depends(get_db)):
    """Get all positions merged across all sleeves for a client"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    perf_svc = PerformanceService(db)
    sleeve_ids = perf_svc.sleeve_ids_for_client(client_id)

    calc_service = PortfolioCalculationService(db)

    pos_result = calc_service.calculate_positions(sleeve_ids) if sleeve_ids else {"open": [], "closed": []}
    merged = pos_result["open"]

    open_positions = (
        db.query(Position)
        .filter(Position.sleeve_id.in_(sleeve_ids), Position.status == "OPEN")
        .all()
    ) if sleeve_ids else []
    raw_prices = perf_svc.fetch_and_persist_prices(open_positions)
    prices = {sym: float(p) for sym, p in raw_prices.items()}

    result_positions = []
    total_cost = Decimal(0)
    total_market_value = Decimal(0)

    for pos in merged:
        symbol = pos["symbol"]
        cost = pos["cost_basis"]
        qty = pos["quantity"]
        avg_cost = cost / qty if qty > 0 else Decimal(0)

        if symbol in prices:
            price = Decimal(str(prices[symbol]))
            market_value = qty * price
            unrealized_gain = market_value - cost
            unrealized_gain_pct = (
                float(unrealized_gain / cost * 100) if cost > 0 else 0.0
            )
        else:
            price = None
            market_value = cost
            unrealized_gain = Decimal(0)
            unrealized_gain_pct = 0.0

        total_cost += cost
        total_market_value += market_value

        result_positions.append(
            {
                "symbol": symbol,
                "quantity": float(qty),
                "cost_basis": float(cost),
                "avg_cost": float(avg_cost),
                "current_price": float(price) if price is not None else None,
                "market_value": float(market_value),
                "unrealized_gain": float(unrealized_gain),
                "unrealized_gain_pct": unrealized_gain_pct,
                "trades_count": pos["trades_count"],
            }
        )

    return {
        "client_id": client_id,
        "total_cost_basis": float(total_cost),
        "total_market_value": float(total_market_value),
        "total_unrealized_gain": float(total_market_value - total_cost),
        "positions_count": len(result_positions),
        "positions": result_positions,
    }


@router.get("/{client_id}/trades")
def get_client_trades(
    client_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get all trades across all sleeves for a client, with pagination"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    base_query = (
        db.query(Trade)
        .join(Sleeve, Trade.sleeve_id == Sleeve.id)
        .join(Account, Sleeve.account_id == Account.id)
        .filter(Account.client_id == client_id)
    )
    total = base_query.count()
    trades = (
        base_query.order_by(Trade.trade_date.desc()).offset(skip).limit(limit).all()
    )

    return {
        "client_id": client_id,
        "total": total,
        "skip": skip,
        "limit": limit,
        "trades": [
            {
                "id": t.id,
                "sleeve_id": t.sleeve_id,
                "trade_date": t.trade_date,
                "symbol": t.symbol,
                "action": t.action,
                "quantity": float(t.quantity),
                "price": float(t.price),
                "commission": float(t.commission),
                "notes": t.notes,
            }
            for t in trades
        ],
    }
