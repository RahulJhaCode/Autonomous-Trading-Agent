"""
agents/bear_researcher.py — Indian market edition (Azure OpenAI).
"""
from __future__ import annotations

from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm_client import get_chat_llm
from config.indian_markets import get_stock
from orchestrator.state import TradingState

SYSTEM_PROMPT = """You are the BEAR Researcher at an Indian equity hedge fund debate session.

Build the strongest BEARISH case AGAINST buying this NSE/BSE listed Indian stock.
Indian bear thesis elements you should leverage:
- Rich valuations vs EM peers (India trades at premium that can compress)
- RBI tightening cycle impact on rate-sensitive sectors (financials, real estate)
- Rupee depreciation risk affecting import-heavy companies
- Promoter pledging and corporate governance risks endemic to Indian markets
- Global FII outflows during risk-off periods (India not immune)
- Regulatory risk from SEBI enforcement and government policy reversals
- Crude oil price spikes (India's Achilles heel — inflation, CAD)
- F&O-driven volatility and short-sellers targeting overvalued stocks

You are BIASED toward bearish. Reference prices in INR (₹).
Keep argument to 200 words. Be rigorous and fear-inducing but data-backed.
"""


def _build_context(state: TradingState) -> str:
    stock = get_stock(state.ticker)
    parts = [
        f"STOCK: {state.ticker} ({stock.name if stock else ''})",
        f"EXCHANGE: NSE | SECTOR: {stock.sector if stock else 'Unknown'}",
    ]
    if state.fundamental_report:
        parts.append(f"\nFUNDAMENTALS:\n{state.fundamental_report.summary}")
    if state.technical_signals:
        parts.append(f"\nTECHNICALS:\n{state.technical_signals.summary}")
    if state.sentiment_score is not None:
        parts.append(f"\nSENTIMENT SCORE: {state.sentiment_score:.2f}\n{state.sentiment_summary[:200]}")
    if state.news_events:
        news = "\n".join(f"  [{e.sentiment}] {e.headline}" for e in state.news_events[:5])
        parts.append(f"\nKEY NEWS:\n{news}")
    return "\n".join(parts)


async def bear_researcher_node(state: TradingState) -> dict:
    ticker = state.ticker
    logger.info(f"[BearResearcher] Building bearish case for {ticker}...")
    llm = get_chat_llm(temperature=0.3, max_tokens=600)

    try:
        context = _build_context(state)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"{context}\n\nBuild the strongest BEARISH case AGAINST buying {ticker} on NSE."),
        ]
        response = await llm.ainvoke(messages)
        logger.success(f"[BearResearcher] Bearish case built for {ticker}")
        return {"bear_argument": response.content, "agent_logs": [f"BearResearcher: Done for {ticker}"]}
    except Exception as e:
        logger.error(f"[BearResearcher]  {e}")
        return {"bear_argument": f"Bear analysis failed: {e}", "errors": [f"BearResearcher error: {e}"]}
