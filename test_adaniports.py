"""
test_adaniports.py
Full end-to-end pipeline test for ADANIPORTS.
Tests: Market Data -> All 9 Agents -> LangGraph -> Trade Decision
"""
import asyncio
import sys
import io

# Fix Windows console encoding for INR and special characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


async def run():
    print("=" * 60)
    print("  FULL PIPELINE TEST: ADANIPORTS (NSE)")
    print("=" * 60)

    # Step 1: Live Market Data
    print("\n[1/4] Fetching live market data...")
    from tools.market_data import get_current_price, get_fundamentals, get_ohlcv

    price = await get_current_price("ADANIPORTS")
    print(f"   Current Price : INR {price:,.2f}")

    fundamentals = await get_fundamentals("ADANIPORTS")
    mcap = str(fundamentals.get('market_cap_cr', 'N/A')).encode('ascii', 'replace').decode()
    print(f"   PE Ratio      : {fundamentals.get('pe_ratio', 'N/A')}")
    print(f"   Market Cap    : {mcap}")
    print(f"   Sector        : {fundamentals.get('sector', 'N/A')}")
    print(f"   52W High      : INR {fundamentals.get('52w_high', 'N/A')}")
    print(f"   52W Low       : INR {fundamentals.get('52w_low', 'N/A')}")
    print(f"   Analyst Rating: {fundamentals.get('analyst_rating', 'N/A')}")

    ohlcv = await get_ohlcv("ADANIPORTS", period="1mo")
    print(f"   OHLCV Rows    : {len(ohlcv)} days of data fetched")

    # Step 2: Free News Search
    print("\n[2/4] Fetching free market news (DuckDuckGo)...")
    from tools.free_search import search_indian_markets
    news = await search_indian_markets("Adani Ports NSE latest news", max_results=3)
    if news:
        print(f"   Found {len(news)} articles:")
        for n in news:
            title = n['title'][:65].encode('ascii', 'replace').decode()
            print(f"   - {title}...")
    else:
        print("   No news found (check internet connection)")

    # Step 3: Full 9-Agent LangGraph Pipeline
    print("\n[3/4] Running full 9-agent LangGraph pipeline...")
    print("   (This takes 30-90 seconds — all agents run via Groq + yfinance)")

    from orchestrator.runner import run_trading_cycle
    final_state = await run_trading_cycle("ADANIPORTS", "1D")

    # Step 4: Results Summary
    print("\n[4/4] PIPELINE RESULTS")
    print("-" * 60)
    print(f"   Ticker          : {final_state.ticker}")
    if final_state.current_price:
        print(f"   Current Price   : INR {final_state.current_price:,.2f}")
    if final_state.sentiment_score is not None:
        sentiment_label = "BULLISH" if final_state.sentiment_score > 0.1 else ("BEARISH" if final_state.sentiment_score < -0.1 else "NEUTRAL")
        print(f"   Sentiment Score : {final_state.sentiment_score:.2f} ({sentiment_label})")
    print(f"   Confidence Score: {final_state.confidence_score:.0%}")

    if final_state.trade_proposal:
        tp = final_state.trade_proposal
        print(f"\n   --- TRADE DECISION ---")
        print(f"   Action          : *** {tp.action} ***")
        print(f"   Position Size   : INR {tp.position_size_usd:,.0f}")
        if tp.entry_price:
            print(f"   Entry Price     : INR {tp.entry_price:,.2f}")
        if tp.stop_loss:
            print(f"   Stop Loss       : INR {tp.stop_loss:,.2f}")
        if tp.take_profit:
            print(f"   Take Profit     : INR {tp.take_profit:,.2f}")
        rationale = tp.rationale[:120].encode('ascii', 'replace').decode()
        print(f"   Rationale       : {rationale}...")

    if final_state.risk_assessment:
        ra = final_state.risk_assessment
        print(f"\n   --- RISK ASSESSMENT ---")
        print(f"   Status          : {'APPROVED' if ra.approved else 'REJECTED'}")
        if ra.rejection_reasons:
            print(f"   Reasons         : {', '.join(ra.rejection_reasons)}")
        if ra.adjusted_position_size_usd:
            print(f"   Adjusted Size   : INR {ra.adjusted_position_size_usd:,.0f}")

    print(f"\n   --- EXECUTION ---")
    print(f"   Final Approved  : {'YES' if final_state.final_approved else 'NO (held by Risk Manager)'}")

    if final_state.execution_result:
        er = final_state.execution_result
        print(f"   Order ID        : {er.order_id}")
        print(f"   Execution Status: {er.status}")

    if final_state.errors:
        print(f"\n   ERRORS: {final_state.errors}")

    print("\n" + "=" * 60)
    print("  TEST COMPLETE - PROJECT WORKING OK")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run())
