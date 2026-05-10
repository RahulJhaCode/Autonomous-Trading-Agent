"""
agents/fundamental_analyst.py
──────────────────────────────
Fundamental Analyst Agent — evaluates financial health, valuation,
earnings quality, and macroeconomic positioning for Indian stocks.
Uses Azure OpenAI (AzureChatOpenAI) via config/llm_client.py.
"""
from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger

from config.llm_client import get_chat_llm
from config.indian_markets import get_stock
from orchestrator.state import TradingState, FundamentalReport
from tools.market_data import get_fundamentals, get_current_price

SYSTEM_PROMPT = """You are an expert Fundamental Analyst specialising in Indian equity markets (NSE/BSE).

You have deep knowledge of Indian accounting standards (Ind AS), SEBI regulations,
RBI monetary policy impact, and sector-specific dynamics in India.

Given the fundamental data of an Indian listed company, you must:
1. Evaluate the company's valuation vs. Indian sector peers (P/E, P/B, EV/EBITDA)
2. Assess earnings quality — watch for promoter pledging, related-party transactions
3. Analyse balance sheet strength in INR context (Debt/Equity, Interest Coverage)
4. Identify Indian-specific catalysts: GST impact, government capex, PLI schemes, RBI rate cycles
5. Note FII/DII ownership trends as a signal of institutional confidence
6. Give a rating: STRONG_BUY / BUY / HOLD / SELL / STRONG_SELL

Always reference market cap in Crores (₹ Cr) and prices in INR.
Output a structured summary in 200 words or less.
"""


async def fundamental_analyst_node(state: TradingState) -> dict:
    """LangGraph node: runs the Fundamental Analyst Agent."""
    ticker = state.ticker
    logger.info(f"[FundamentalAnalyst] Analyzing {ticker} (Indian market)...")

    llm = get_chat_llm(temperature=0.1, max_tokens=600)

    try:
        # Gather data
        fundamentals = await get_fundamentals(ticker)
        current_price = await get_current_price(ticker)
        stock_meta = get_stock(ticker)

        index_info = ""
        if stock_meta:
            indices = []
            if stock_meta.nifty50:  indices.append("Nifty 50")
            if stock_meta.sensex30: indices.append("Sensex 30")
            index_info = f"Index Membership: {', '.join(indices) if indices else 'None'}"

        data_str = "\n".join(
            f"  {k.replace('_', ' ').title()}: {v}"
            for k, v in fundamentals.items()
            if v is not None
        )

        human_msg = f"""Analyse {ticker} ({stock_meta.name if stock_meta else ticker}) listed on NSE.

{index_info}
Sector: {stock_meta.sector if stock_meta else 'Unknown'}

Fundamental Data:
{data_str}

Current Market Price: ₹{f'{current_price:,.2f}' if current_price else 'N/A'}

Provide your fundamental analysis and rating for this Indian listed company."""

        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=human_msg)]
        response = await llm.ainvoke(messages)
        analysis_text = response.content

        report = FundamentalReport(
            pe_ratio=fundamentals.get("pe_ratio"),
            eps=fundamentals.get("eps"),
            revenue_growth_yoy=fundamentals.get("revenue_growth"),
            debt_to_equity=fundamentals.get("debt_to_equity"),
            free_cash_flow=fundamentals.get("free_cash_flow"),
            analyst_rating=fundamentals.get("analyst_rating", "hold"),
            summary=analysis_text,
        )

        logger.success(f"[FundamentalAnalyst] {ticker} analysis complete")
        return {
            "fundamental_report": report,
            "current_price":      current_price,
            "agent_logs":         [f"FundamentalAnalyst: Completed for {ticker} ({index_info})"],
        }

    except Exception as e:
        logger.error(f"[FundamentalAnalyst] Error: {e}")
        return {
            "fundamental_report": FundamentalReport(summary=f"Analysis failed: {e}"),
            "errors": [f"FundamentalAnalyst error: {e}"],
        }
