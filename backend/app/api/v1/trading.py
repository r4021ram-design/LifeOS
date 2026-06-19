from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from typing import List
import datetime
from app.core.db import get_db
from app.api.v1.auth import get_current_user
from app.models.models import User, TradingJournal
from app.schemas.schemas import TradingJournalCreate, TradingJournalUpdate, TradingJournalResponse

router = APIRouter(prefix="/trading", tags=["trading"])

@router.get("/journal", response_model=List[TradingJournalResponse])
def list_trades(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(TradingJournal).filter(TradingJournal.user_id == current_user.id).all()

@router.post("/journal", response_model=TradingJournalResponse, status_code=status.HTTP_201_CREATED)
def log_trade(trade_in: TradingJournalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_trade = TradingJournal(
        user_id=current_user.id,
        ticker=trade_in.ticker,
        type=trade_in.type,
        quantity=trade_in.quantity,
        entry_price=trade_in.entry_price,
        strategy=trade_in.strategy,
        psychology_notes=trade_in.psychology_notes
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

@router.put("/journal/{trade_id}", response_model=TradingJournalResponse)
def exit_trade(
    trade_id: int,
    trade_in: TradingJournalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_trade = db.query(TradingJournal).filter(TradingJournal.id == trade_id, TradingJournal.user_id == current_user.id).first()
    if not db_trade:
        raise HTTPException(status_code=404, detail="Trade log not found")

    if trade_in.exit_price is not None:
        db_trade.exit_price = trade_in.exit_price
        db_trade.exit_time = trade_in.exit_time or datetime.datetime.now(datetime.UTC)
        multiplier = 1 if db_trade.type.lower() == "long" else -1
        db_trade.pnl = (db_trade.exit_price - db_trade.entry_price) * db_trade.quantity * multiplier

    if trade_in.psychology_notes is not None:
        db_trade.psychology_notes = trade_in.psychology_notes

    db.commit()
    db.refresh(db_trade)
    return db_trade
