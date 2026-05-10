"""api/routes/trades.py — Trade history and log endpoints."""
from fastapi import APIRouter

router = APIRouter()

# In-memory trade log (replace with PostgreSQL in production)
_trade_log: list[dict] = []

@router.get("/")
async def get_trades():
    return {"trades": _trade_log, "total": len(_trade_log)}

@router.get("/summary")
async def get_summary():
    buys  = [t for t in _trade_log if t.get("action") == "BUY"]
    sells = [t for t in _trade_log if t.get("action") == "SELL"]
    return {"total_trades": len(_trade_log), "buys": len(buys), "sells": len(sells)}
