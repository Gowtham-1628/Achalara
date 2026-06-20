"""Trade endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.trade import Trade
from app.models.sleeve import Sleeve
from app.api.schemas.trade import TradeCreate, TradeResponse

router = APIRouter()


@router.post("/", response_model=TradeResponse, status_code=201)
def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    """Create a new trade"""
    sleeve = db.query(Sleeve).filter(Sleeve.id == trade.sleeve_id).first()
    if not sleeve:
        raise HTTPException(status_code=404, detail="Sleeve not found")

    db_trade = Trade(
        sleeve_id=trade.sleeve_id,
        trade_date=trade.trade_date,
        symbol=trade.symbol,
        action=trade.action,
        quantity=trade.quantity,
        price=trade.price,
        commission=trade.commission,
        notes=trade.notes,
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)

    # Recompute weekly snapshots for this sleeve from the new trade's week onward.
    try:
        from app.services.weekly_snapshot_service import WeeklySnapshotService
        WeeklySnapshotService(db).recompute_from(trade.sleeve_id, trade.trade_date)
    except Exception:
        pass  # snapshot failure must never block trade creation

    return db_trade
