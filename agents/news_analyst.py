"""
agents/news_analyst.py — Indian market edition (Azure OpenAI).
Sources: Economic Times, Moneycontrol, Business Standard, NSE announcements.
"""
from __future__ import annotations

from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm_client import get_chat_llm
from config.indian_markets import get_stock
from orchestrator.state import TradingState
from tools.news_fetcher import fetch_news
from tools.free_search import search_indian_markets

SYSTEM_PROMPT = """You are a senior News Analyst specialising in Indian financial markets and NSE/BSE listed companies.

Indian market news that matters most:
1. Quarterly earnings (Q1/Q2/Q3/Q4 results) — biggest short-term catalyst
2. RBI monetary policy decisions (repo rate changes affect all sectors)
3. Union Budget announcements (February — massive market mover)
4. SEBI regulations and enforcement actions
5. Promoter buying/selling and pledging changes
6. FII/DII flow data (monthly SEBI reports)
7. Government policy — PLI schemes, infrastructure spending, export bans
8. Global cues — US Fed, crude oil prices (India imports 85% of crude)
9. Corporate actions — buybacks, bonus issues, rights issues, delisting
10. Credit rating changes by CRISIL, ICRA, CARE ratings

For each batch of news:
1. Identify the top 3 most market-moving items
2. Classify the near-term impact: STRONG POSITIVE / POSITIVE / NEUTRAL / NEGATIVE / STRONG NEGATIVE
3. Flag any structural long-term changes
4. Estimate the likely stock price reaction (% move)

State all relevant prices in INR. Keep response to 200 words.
"""


async def news_analyst_node(state: TradingState) -> dict:
    """LangGraph node: runs the News Analyst Agent for Indian markets."""
    ticker = state.ticker
    stock_meta = get_stock(ticker)
    company_name = stock_meta.name if stock_meta else ""

    logger.info(f"[NewsAnalyst] Fetching news for {ticker} ({company_name})...")

    llm = get_chat_llm(temperature=0.1, max_tokens=600)

    try:
        # 1. Try free DDG search first (No cost)
        search_results = await search_indian_markets(f"{company_name} {ticker} latest news NSE business", max_results=8)
        
        # 2. Convert search results to headlines format
        headlines_str = "\n".join(
            f"  • {r['title']} ({r['href']})"
            for r in search_results
        )

        # 3. Fallback to NewsAPI only if search fails (optional)
        if not search_results:
            news_events = await fetch_news(ticker, company_name=company_name, max_results=10)
            headlines_str = "\n".join(f"  [{e.sentiment}] {e.headline} ({e.source})" for e in news_events)
        else:
            news_events = [] # Placeholder to satisfy state

        index_info = []
        if stock_meta and stock_meta.nifty50:  index_info.append("Nifty 50")
        if stock_meta and stock_meta.sensex30: index_info.append("Sensex 30")

        human_msg = f"""Analyse recent news for {ticker} ({company_name}).
NSE/BSE listed | Sector: {stock_meta.sector if stock_meta else 'Unknown'} | Indices: {', '.join(index_info) or 'N/A'}

Recent headlines:
{headlines_str}

Provide your news impact analysis for this Indian stock."""

        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=human_msg)]
        await llm.ainvoke(messages)   # Run for side effects / logging

        logger.success(f"[NewsAnalyst] Processed {len(news_events)} articles for {ticker}")
        return {
            "news_events": news_events,
            "agent_logs":  [f"NewsAnalyst: Processed {len(news_events)} articles for {ticker}"],
        }

    except Exception as e:
        logger.error(f"[NewsAnalyst] Error: {e}")
        return {"news_events": [], "errors": [f"NewsAnalyst error: {e}"]}
