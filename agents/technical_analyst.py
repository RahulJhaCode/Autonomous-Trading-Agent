"""
agents/technical_analyst.py — Indian market edition (Azure OpenAI).
"""
from __future__ import annotations

from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm_client import get_chat_llm
from config.indian_markets import get_stock
from orchestrator.state import TradingState
from tools.market_data import get_ohlcv
from tools.technical_indicators import compute_indicators

SYSTEM_PROMPT = """You are a world-class Technical Analyst specialising in NSE/BSE Indian equity markets.

Indian market-specific technical context:
- NSE market hours: 9:15 AM – 3:30 PM IST
- Key support/resistance often at round INR numbers (₹500, ₹1000, ₹2000)
- High F&O activity on Nifty 50 stocks — options open interest is a key sentiment tool
- Watch for "circuit breakers" — stocks hit 5%/10%/20% daily limits in India
- Nifty Bank and Nifty IT sector indices heavily influence individual stock moves
- Thursday is monthly F&O expiry — volatility spikes

Given technical indicators, you must:
1. Identify primary trend with respect to key Indian indices (Nifty 50 position)
2. Spot support/resistance at key INR price levels
3. Interpret RSI momentum for Indian market conditions
4. Assess MACD crossovers with respect to recent earnings cycle
5. Suggest entry/exit in INR with specific price levels

State all prices in INR (₹). Keep analysis to 200 words.
"""


async def technical_analyst_node(state: TradingState) -> dict:
    """LangGraph node: runs the Technical Analyst Agent."""
    ticker = state.ticker
    stock_meta = get_stock(ticker)
    logger.info(f"[TechnicalAnalyst] Computing indicators for {ticker}...")

    llm = get_chat_llm(temperature=0.05, max_tokens=600)

    try:
        df = await get_ohlcv(ticker, period="6mo", interval="1d")
        if df.empty:
            raise ValueError(f"No OHLCV data for {ticker}")

        signals = compute_indicators(df)

        human_msg = f"""Analyse {ticker} ({stock_meta.name if stock_meta else ticker}) — NSE listed.
Sector: {stock_meta.sector if stock_meta else 'Unknown'}
Index: {'Nifty 50' if stock_meta and stock_meta.nifty50 else ''} {'Sensex 30' if stock_meta and stock_meta.sensex30 else ''}

Technical Data (prices in INR ₹):
  RSI(14): {f"{signals.rsi_14:.1f}" if signals.rsi_14 else "N/A"}
  MACD: {f"{signals.macd:.4f}" if signals.macd else "N/A"}
  MACD Signal: {f"{signals.macd_signal:.4f}" if signals.macd_signal else "N/A"}
  Bollinger Upper: ₹{f"{signals.bb_upper:.2f}" if signals.bb_upper else "N/A"}
  Bollinger Lower: ₹{f"{signals.bb_lower:.2f}" if signals.bb_lower else "N/A"}
  SMA 50: ₹{f"{signals.sma_50:.2f}" if signals.sma_50 else "N/A"}
  SMA 200: ₹{f"{signals.sma_200:.2f}" if signals.sma_200 else "N/A"}
  Overall Trend: {signals.trend}

Provide your technical analysis with specific INR entry/exit price recommendations."""

        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=human_msg)]
        response = await llm.ainvoke(messages)
        signals.summary = response.content

        logger.success(f"[TechnicalAnalyst] {ticker} — trend: {signals.trend}")
        return {
            "technical_signals": signals,
            "agent_logs": [f"TechnicalAnalyst: Trend={signals.trend}, RSI={f'{signals.rsi_14:.1f}' if signals.rsi_14 else 'N/A'}"],
        }

    except Exception as e:
        logger.error(f"[TechnicalAnalyst] Error: {e}")
        return {"technical_signals": None, "errors": [f"TechnicalAnalyst error: {e}"]}
