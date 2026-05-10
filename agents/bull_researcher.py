"""
agents/bull_researcher.py — Indian market edition (Azure OpenAI).
"""
from __future__ import annotations

from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm_client import get_chat_llm
from config.indian_markets import get_stock
from orchestrator.state import TradingState

SYSTEM_PROMPT = """You are the BULL Researcher at an Indian equity hedge fund debate session.

Build the strongest BULLISH case for buying this NSE/BSE listed Indian stock.
Indian bull thesis elements you should leverage:
- India's GDP growth story (fastest-growing major economy)
- Demographic dividend and rising middle class consumption
- Government capex cycle and infrastructure buildout
- PLI (Production-Linked Incentive) scheme tailwinds
- Formalisation of the economy benefiting organised sector players
- FII re-rating potential as India gains EM index weight
- Strong domestic mutual fund SIP flows providing market support

You are BIASED toward bullish. Reference prices in INR (₹).
Keep argument to 200 words. Be passionate but data-backed.
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


async def bull_researcher_node(state: TradingState) -> dict:
    ticker = state.ticker
    logger.info(f"[BullResearcher] Building bullish case for {ticker}...")
    llm = get_chat_llm(temperature=0.3, max_tokens=600)

    try:
        context = _build_context(state)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"{context}\n\nBuild the strongest BULLISH case for buying {ticker} on NSE now."),
        ]
        response = await llm.ainvoke(messages)
        logger.success(f"[BullResearcher]  Bullish case built for {ticker}")
        return {"bull_argument": response.content, "agent_logs": [f"BullResearcher: Done for {ticker}"]}
    except Exception as e:
        logger.error(f"[BullResearcher]  {e}")
        return {"bull_argument": f"Bull analysis failed: {e}", "errors": [f"BullResearcher error: {e}"]}
