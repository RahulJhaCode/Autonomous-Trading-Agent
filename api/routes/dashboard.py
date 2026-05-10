"""api/routes/dashboard.py — Dashboard data endpoints."""
from fastapi import APIRouter
from tools.market_data import get_current_price, get_fundamentals

router = APIRouter()

@router.get("/portfolio")
async def get_portfolio():
    return {"portfolio_value": 100_000, "cash": 100_000, "positions": [], "pnl": 0.0}

@router.get("/quote/{ticker}")
async def get_quote(ticker: str):
    price = await get_current_price(ticker.upper())
    return {"ticker": ticker.upper(), "price": price}
