"""
orchestrator/runner.py
──────────────────────
Entry point to run a full trading analysis cycle for a given ticker.
"""
from __future__ import annotations

import asyncio
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from orchestrator.graph import trading_graph
from orchestrator.state import TradingState

# Force UTF-8 safe console — fixes Windows cp1252 emoji crash when run via uvicorn
console = Console(highlight=False, emoji=False, markup=True)


async def run_trading_cycle(ticker: str, timeframe: str = "1D") -> TradingState:
    """
    Execute a full autonomous trading cycle for the given ticker.
    Returns the final TradingState after all agents have run.
    """
    logger.info(f"[Runner] Starting trading cycle: {ticker} ({timeframe})")

    initial_state = TradingState(ticker=ticker, timeframe=timeframe)

    # Stream events for live logging
    final_state = None
    async for event in trading_graph.astream(initial_state, stream_mode="values"):
        final_state = event
        event_dict = event.model_dump() if hasattr(event, 'model_dump') else {}
        completed = [
            k for k, v in event_dict.items()
            if v is not None and k not in ("ticker", "timeframe", "portfolio_value")
        ]
        if completed:
            logger.debug(f"State updated -- fields: {completed}")

    # Ensure final_state is a TradingState instance (LangGraph may return dict)
    if final_state is not None and isinstance(final_state, dict):
        final_state = TradingState(**final_state)

    _print_summary(final_state)
    return final_state


def _print_summary(state: TradingState) -> None:
    """Print a rich summary table of the trading cycle result."""
    table = Table(title="Trading Cycle Summary", show_header=True, header_style="bold magenta")
    table.add_column("Field",  style="cyan",  width=28)
    table.add_column("Value",  style="white")

    table.add_row("Ticker",           state.ticker)
    table.add_row("Timeframe",        state.timeframe)
    table.add_row("Current Price",    f"INR {state.current_price:,.2f}" if state.current_price else "N/A")
    table.add_row("Sentiment Score",  f"{state.sentiment_score or 0:.2f} (-1=bearish, +1=bullish)")
    table.add_row("Confidence Score", f"{state.confidence_score:.2%}")

    if state.trade_proposal:
        tp = state.trade_proposal
        action_markup = (
            f"[bold green]{tp.action}[/bold green]" if tp.action == "BUY"
            else f"[bold red]{tp.action}[/bold red]" if tp.action == "SELL"
            else f"[yellow]{tp.action}[/yellow]"
        )
        table.add_row("Trade Action",  action_markup)
        table.add_row("Position Size", f"INR {tp.position_size_usd:,.2f}")
        table.add_row("Take Profit",   f"INR {tp.take_profit:,.2f}" if tp.take_profit else "--")
        table.add_row("Stop Loss",     f"INR {tp.stop_loss:,.2f}"   if tp.stop_loss   else "--")

    if state.risk_assessment:
        ra = state.risk_assessment
        status = "[bold green]APPROVED[/bold green]" if ra.approved else "[bold red]REJECTED[/bold red]"
        table.add_row("Risk Assessment", status)
        if ra.rejection_reasons:
            table.add_row("Rejection Reasons", ", ".join(ra.rejection_reasons))

    table.add_row("Final Approved", "[bold green]YES[/bold green]" if state.final_approved else "[red]NO[/red]")

    if state.execution_result and state.execution_result.order_id:
        er = state.execution_result
        table.add_row("Order ID",        er.order_id or "--")
        table.add_row("Execution Price", f"INR {er.filled_price:,.2f}" if er.filled_price else "--")
        table.add_row("Filled Qty",      str(er.filled_qty))

    console.print(table)

    if state.errors:
        console.print(Panel(", ".join(state.errors), title="Errors", border_style="red"))


if __name__ == "__main__":
    asyncio.run(run_trading_cycle("RELIANCE", "1D"))
