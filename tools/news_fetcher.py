"""
tools/news_fetcher.py
─────────────────────
Fetches news headlines from NewsAPI and processes them for agent consumption.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from loguru import logger

from config.settings import settings
from orchestrator.state import NewsEvent


async def fetch_news(ticker: str, company_name: str = "", max_results: int = 10) -> list[NewsEvent]:
    """Fetch recent news for a ticker from NewsAPI."""
    query = f"{ticker} OR {company_name}" if company_name else ticker
    url = "https://newsapi.org/v2/everything"
    params = {
        "q":          query,
        "sortBy":     "publishedAt",
        "language":   "en",
        "pageSize":   max_results,
        "from":       (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "apiKey":     settings.news_api_key,
    }

    if not settings.news_api_key:
        logger.warning("NEWS_API_KEY not set — returning mock news")
        return _mock_news(ticker)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.warning(f"NewsAPI returned status {resp.status}")
                    return _mock_news(ticker)
                data = await resp.json()
                articles = data.get("articles", [])
                return [_parse_article(a) for a in articles[:max_results]]
    except Exception as e:
        logger.error(f"News fetch error for {ticker}: {e}")
        return _mock_news(ticker)


def _parse_article(article: dict[str, Any]) -> NewsEvent:
    """Convert a NewsAPI article dict into a NewsEvent model."""
    title = article.get("title", "")
    sentiment = _simple_sentiment(title)
    return NewsEvent(
        headline=title,
        source=article.get("source", {}).get("name", "Unknown"),
        sentiment=sentiment,
        relevance_score=0.7,  # Default; can be enhanced with LLM scoring
        published_at=article.get("publishedAt", ""),
    )


def _simple_sentiment(text: str) -> str:
    """Keyword-based sentiment classification (upgraded by agents via LLM)."""
    text_lower = text.lower()
    positive_keywords = ["beat", "surge", "profit", "growth", "bullish", "upgrade", "buy", "record", "strong"]
    negative_keywords = ["miss", "drop", "loss", "crash", "bearish", "downgrade", "sell", "warn", "weak", "layoff"]

    pos = sum(1 for w in positive_keywords if w in text_lower)
    neg = sum(1 for w in negative_keywords if w in text_lower)

    if pos > neg:   return "POSITIVE"
    elif neg > pos: return "NEGATIVE"
    return "NEUTRAL"


def _mock_news(ticker: str) -> list[NewsEvent]:
    """Return mock news when API key is not configured."""
    return [
        NewsEvent(
            headline=f"{ticker}: Strong quarterly earnings beat analyst expectations",
            source="Mock Financial News",
            sentiment="POSITIVE",
            relevance_score=0.9,
            published_at=datetime.now().isoformat(),
        ),
        NewsEvent(
            headline=f"{ticker} faces regulatory scrutiny in key markets",
            source="Mock Financial News",
            sentiment="NEGATIVE",
            relevance_score=0.7,
            published_at=datetime.now().isoformat(),
        ),
    ]
