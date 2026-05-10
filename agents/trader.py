"""
agents/trader.py — Indian market edition (Groq LLM).
All position sizes and prices in INR (Indian Rupees).
"""
from __future__ import annotations

import re
from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm_client import get_chat_llm
from config.indian_markets import get_stock
from config.settings import settings
from orchestrator.state import TradingState, TradeProposal

SYSTEM_PROMPT = """You are the Head Trader at an elite Indian equity hedge fund operating on NSE/BSE.

You trade Indian listed stocks. All prices and position sizes are in INR (Indian Rupees).

The portfolio is worth INR 10,00,000 (10 Lakhs). Your position size must be:
- BUY/SELL: Between INR 20,000 and INR 50,000 (2% to 5% of portfolio per trade)
- HOLD: POSITION_SIZE_INR must be 0

Indian trading rules:
- Minimum 1 share (no fractional shares on NSE)
- T+1 settlement (equity delivery)
- Circuit limits: 5%/10%/20% price bands apply
- Stop loss must be 2-4% below entry for BUY orders
- Take profit must be 4-8% above entry for BUY orders

Based on all analyst reports, generate your trading decision.

Use this EXACT format — no extra text:
ACTION: [BUY | SELL | HOLD]
POSITION_SIZE_INR: [integer amount in INR, e.g. 35000]
ENTRY_PRICE_INR: [price in INR as a number, e.g. 1760.40 — or MARKET]
TAKE_PROFIT_INR: [target price in INR as a number, e.g. 1900.00]
STOP_LOSS_INR: [stop loss in INR as a number, e.g. 1690.00]
CONFIDENCE: [0.0 to 1.0]
RATIONALE: [2 sentences max]
"""


def _parse_trade_proposal(text: str, portfolio_value: float) -> tuple[TradeProposal, float]:
    def extract(pattern, default=None):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else default

    action_str = extract(r"ACTION:\s*(BUY|SELL|HOLD)", "HOLD")
    size_str   = extract(r"POSITION_SIZE_INR:\s*([\d,.]+)", "0")
    entry_str  = extract(r"ENTRY_PRICE_INR:\s*([\d.]+|MARKET)", None)
    tp_str     = extract(r"TAKE_PROFIT_INR:\s*([\d.]+|N/A)", None)
    sl_str     = extract(r"STOP_LOSS_INR:\s*([\d.]+|N/A)", None)
    conf_str   = extract(r"CONFIDENCE:\s*([\d.]+)", "0.5")
    rationale  = extract(r"RATIONALE:\s*(.+)", "No rationale provided.")

    try:
        size = float(str(size_str).replace(",", ""))
    except (ValueError, TypeError):
        size = 0.0

    max_size = portfolio_value * (settings.max_position_size_pct / 100)  # e.g. 50,000 for 5%
    min_size = portfolio_value * 0.02  # Minimum 2% = 20,000 INR per trade

    # Clamp within [min_size, max_size] — but only if action is BUY/SELL
    if action_str in ("BUY", "SELL") and size > 0:
        size = max(min_size, min(size, max_size))
    elif action_str == "HOLD":
        size = 0.0

    proposal = TradeProposal(
        action=action_str,
        position_size_usd=size,   # Field reused for INR
        entry_price=float(entry_str) if entry_str and entry_str not in ("MARKET", "N/A") else None,
        take_profit=float(tp_str) if tp_str and tp_str not in ("N/A", "MARKET") else None,
        stop_loss=float(sl_str)   if sl_str  and sl_str  not in ("N/A", "MARKET") else None,
        rationale=rationale or "",
    )
    confidence = max(0.0, min(1.0, float(conf_str or 0.5)))
    return proposal, confidence


async def trader_node(state: TradingState) -> dict:
    """LangGraph node: Trader Agent for Indian markets."""
    ticker = state.ticker
    stock_meta = get_stock(ticker)
    logger.info(f"[Trader] Synthesizing trade decision for {ticker}...")

    llm = get_chat_llm(temperature=0.05, max_tokens=512)

    try:
        human_msg = f"""TICKER: {ticker} ({stock_meta.name if stock_meta else ''})
EXCHANGE: NSE | SECTOR: {stock_meta.sector if stock_meta else 'Unknown'}
CURRENT PRICE: ₹{f'{state.current_price:,.2f}' if state.current_price else 'Unknown'}
PORTFOLIO VALUE: ₹{state.portfolio_value:,.2f}
INDEX MEMBERSHIP: {'Nifty 50 ' if stock_meta and stock_meta.nifty50 else ''}{'Sensex 30' if stock_meta and stock_meta.sensex30 else ''}

FUNDAMENTAL REPORT:
{state.fundamental_report.summary if state.fundamental_report else 'Not available'}

TECHNICAL REPORT:
{state.technical_signals.summary if state.technical_signals else 'Not available'}

SENTIMENT SCORE: {f"{state.sentiment_score:.2f}" if state.sentiment_score is not None else 'N/A'}
{state.sentiment_summary[:300] if state.sentiment_summary else ''}

NEWS ({len(state.news_events)} items):
{chr(10).join(f"  [{e.sentiment}] {e.headline}" for e in state.news_events[:5])}

BULL CASE: {state.bull_argument[:400] if state.bull_argument else 'N/A'}
BEAR CASE: {state.bear_argument[:400] if state.bear_argument else 'N/A'}

Make your trading decision. All prices and sizes must be in INR (₹)."""

        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=human_msg)]
        response = await llm.ainvoke(messages)

        proposal, confidence = _parse_trade_proposal(response.content, state.portfolio_value)

        logger.success(
            f"[Trader] {proposal.action} {ticker} | "
            f"₹{proposal.position_size_usd:,.0f} | Conf: {confidence:.0%}"
        )
        return {
            "trade_proposal":   proposal,
            "confidence_score": confidence,
            "research_summary": response.content,
            "agent_logs": [f"Trader: {proposal.action} {ticker} ₹{proposal.position_size_usd:,.0f} | {confidence:.0%}"],
        }

    except Exception as e:
        logger.error(f"[Trader] Error: {e}")
        return {
            "trade_proposal":   TradeProposal(action="HOLD", rationale=f"Error: {e}"),
            "confidence_score": 0.0,
            "errors":           [f"Trader error: {e}"],
        }
