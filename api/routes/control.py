"""
api/routes/control.py
─────────────────────
Control endpoints — start / stop trading cycles and configure settings.
"""
from __future__ import annotations

import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from orchestrator.runner import run_trading_cycle
from api.websocket_manager import ws_manager
from config.indian_markets import resolve_ticker

router = APIRouter()

# Track running tasks
_running_tasks: dict[str, asyncio.Task] = {}


class RunCycleRequest(BaseModel):
    ticker: str
    timeframe: str = "1D"


@router.post("/run")
async def start_trading_cycle(req: RunCycleRequest, background_tasks: BackgroundTasks):
    """Start a full trading analysis cycle for a ticker in the background."""
    raw_input = req.ticker.strip().upper()

    # Resolve company name or symbol → correct NSE ticker
    # e.g. "INFOSYS" → "INFY", "Reliance" → "RELIANCE", "TCS" → "TCS"
    resolved_ticker_ns, stock_meta = resolve_ticker(raw_input)
    # Use clean symbol (without .NS) for internal tracking
    ticker = resolved_ticker_ns.replace(".NS", "")

    resolved_name = stock_meta.name if stock_meta else ticker

    if ticker in _running_tasks and not _running_tasks[ticker].done():
        raise HTTPException(status_code=409, detail=f"Cycle already running for {ticker}")

    async def _run():
        await ws_manager.broadcast({
            "type": "cycle_started",
            "ticker": ticker,
            "company": resolved_name,
        })
        result = await run_trading_cycle(ticker, req.timeframe)
        await ws_manager.broadcast({
            "type":    "cycle_completed",
            "ticker":  ticker,
            "company": resolved_name,
            "action":  result.trade_proposal.action if result.trade_proposal else "HOLD",
            "confidence": result.confidence_score,
            "approved": result.final_approved,
            "price":   result.current_price,
        })

    task = asyncio.create_task(_run())
    _running_tasks[ticker] = task
    return {
        "status": "started",
        "ticker": ticker,
        "company": resolved_name,
        "resolved_from": raw_input,
    }


@router.post("/stop/{ticker}")
async def stop_trading_cycle(ticker: str):
    """Cancel a running trading cycle."""
    ticker = ticker.upper()
    task = _running_tasks.get(ticker)
    if task and not task.done():
        task.cancel()
        return {"status": "cancelled", "ticker": ticker}
    raise HTTPException(status_code=404, detail=f"No running cycle for {ticker}")


@router.get("/status")
async def get_status():
    """Return status of all running cycles."""
    return {
        ticker: "running" if not task.done() else "completed"
        for ticker, task in _running_tasks.items()
    }
