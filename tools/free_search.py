"""
tools/free_search.py
────────────────────
Completely free web search tool for Indian market research.
Uses DuckDuckGo via the 'ddgs' package (successor to duckduckgo_search).
Falls back to a simple HTTP scrape if ddgs is unavailable.
"""
from loguru import logger
import asyncio


async def search_indian_markets(query: str, max_results: int = 5) -> list[dict]:
    """
    Search for Indian market news and reports for free.
    Returns a list of dicts with 'title', 'href' (link), and 'body' (snippet).
    """
    logger.info(f"🔍 Free Search (DDG): {query}")

    # Try the modern 'ddgs' package first
    try:
        from ddgs import DDGS
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: list(DDGS().text(query, region='in-en', safesearch='off', timelimit='w', max_results=max_results))
        )
        if results:
            logger.debug(f"DDG (ddgs) returned {len(results)} results")
            return results
    except ImportError:
        logger.debug("'ddgs' package not installed, trying legacy 'duckduckgo_search'")
    except Exception as e:
        logger.warning(f"ddgs search failed: {e}")

    # Fallback: try the old 'duckduckgo_search' package
    try:
        from duckduckgo_search import DDGS as LegacyDDGS
        with LegacyDDGS() as ddgs:
            results = list(ddgs.text(query, region='in-en', safesearch='off', timelimit='w', max_results=max_results))
        if results:
            logger.debug(f"DDG (legacy) returned {len(results)} results")
            return results
    except ImportError:
        logger.debug("'duckduckgo_search' package not installed either")
    except Exception as e:
        logger.warning(f"Legacy DDG search failed: {e}")

    # Final fallback: return empty (agents will use their own mock/fallback logic)
    logger.warning("All search providers failed — returning empty results")
    return []


if __name__ == "__main__":
    # Quick test
    res = asyncio.run(search_indian_markets("Reliance Industries latest news NSE"))
    for r in res:
        print(f"- {r['title']}\n  {r['href']}\n")
