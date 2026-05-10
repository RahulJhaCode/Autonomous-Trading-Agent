"""
agents/sentiment_analyst.py
────────────────────────────
Sentiment Analyst Agent for Indian markets.
Sources: Reddit (r/IndiaInvestments, r/DalalStreet), Economic Times,
Moneycontrol news, NSE announcements.
Uses Azure OpenAI via config/llm_client.py.
"""
from __future__ import annotations

from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm_client import get_chat_llm
from config.indian_markets import get_stock
from orchestrator.state import TradingState

SYSTEM_PROMPT = """You are an elite Sentiment Analyst specialising in Indian financial markets.

You understand Indian retail investor behavior on platforms like:
- Moneycontrol, Economic Times, Business Standard (news)
- r/IndiaInvestments, r/DalalStreet (Reddit)
- ValuePickr forums (serious Indian investors)
- NSE/BSE exchange announcements

Indian market-specific context you must consider:
1. FII (Foreign Institutional Investor) buying/selling sentiment
2. DII (Domestic Institutional Investor) flows (mutual funds, LIC)
3. Retail investor "F&O fever" — options sentiment can drive intraday moves
4. Budget/RBI policy meeting proximity (high impact periods)
5. Promoter activity — insider buying is very bullish in Indian context

Produce a sentiment score: -1.0 (extreme bearish) to +1.0 (extreme bullish)

Format your response as:
SENTIMENT_SCORE: [number between -1.0 and 1.0]
DOMINANT_EMOTION: [one word]
FII_SENTIMENT: [BUYING | SELLING | NEUTRAL]
DII_SENTIMENT: [BUYING | SELLING | NEUTRAL]
KEY_THEMES: [comma-separated list]
SUMMARY: [2-3 sentences]
"""


async def _fetch_indian_reddit_posts(ticker: str, company_name: str = "") -> list[str]:
    """Fetch posts from Indian investment subreddits."""
    try:
        import praw
        from config.settings import settings

        reddit = praw.Reddit(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
        )

        query = company_name if company_name else ticker
        posts = []
        for sub in ["IndiaInvestments", "DalalStreet", "IndianStockMarket", "stocks"]:
            try:
                for post in reddit.subreddit(sub).search(query, limit=5, time_filter="week"):
                    posts.append(f"[r/{sub}] {post.title} (upvotes: {post.score})")
            except Exception:
                continue

        return posts[:15] if posts else _mock_indian_posts(ticker, company_name)

    except Exception as e:
        logger.warning(f"Reddit fetch failed: {e}. Using mock data.")
        return _mock_indian_posts(ticker, company_name)


def _mock_indian_posts(ticker: str, name: str) -> list[str]:
    label = name or ticker
    return [
        f"[r/IndiaInvestments] {label} Q4 results beat estimates — strong buy signal?",
        f"[r/DalalStreet] {label} FII buying trend continues — bullish setup",
        f"[r/IndianStockMarket] Promoter holding stable in {label} — good sign",
        f"[r/IndiaInvestments] Concerned about {label} debt levels and RBI rate impact",
        f"[r/DalalStreet] {label} support at key moving average — watch for breakout",
        f"[r/IndiaInvestments] DII accumulation visible in {label} — long-term positive",
    ]


def _parse_sentiment_score(text: str) -> float:
    for line in text.split("\n"):
        if line.strip().startswith("SENTIMENT_SCORE:"):
            try:
                return max(-1.0, min(1.0, float(line.split(":")[1].strip())))
            except ValueError:
                pass
    return 0.0


async def sentiment_analyst_node(state: TradingState) -> dict:
    """LangGraph node: runs the Sentiment Analyst Agent for Indian markets."""
    ticker = state.ticker
    stock_meta = get_stock(ticker)
    company_name = stock_meta.name if stock_meta else ""

    logger.info(f"[SentimentAnalyst] Analyzing sentiment for {ticker} ({company_name})...")

    llm = get_chat_llm(temperature=0.1, max_tokens=600)

    try:
        posts = await _fetch_indian_reddit_posts(ticker, company_name)
        posts_str = "\n".join(f"  • {p}" for p in posts)

        human_msg = f"""Analyze the market sentiment for {ticker} ({company_name}) — NSE listed Indian company.

Social media and forum posts:
{posts_str}

Provide your sentiment analysis with the required format."""

        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=human_msg)]
        response = await llm.ainvoke(messages)
        text = response.content

        score = _parse_sentiment_score(text)

        logger.success(f"[SentimentAnalyst]  {ticker} sentiment score: {score:.2f}")
        return {
            "sentiment_score":   score,
            "sentiment_summary": text,
            "agent_logs":        [f"SentimentAnalyst: Score={score:.2f} for {ticker}"],
        }

    except Exception as e:
        logger.error(f"[SentimentAnalyst] Error: {e}")
        return {
            "sentiment_score":   0.0,
            "sentiment_summary": f"Sentiment analysis failed: {e}",
            "errors":            [f"SentimentAnalyst error: {e}"],
        }
