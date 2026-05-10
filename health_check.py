"""
health_check.py
Comprehensive project health check — run before starting the system.
Usage: python health_check.py
"""
import sys

errors = []

print("[1/5] Checking agent imports...")
try:
    from agents.fundamental_analyst import fundamental_analyst_node
    from agents.sentiment_analyst import sentiment_analyst_node
    from agents.technical_analyst import technical_analyst_node
    from agents.news_analyst import news_analyst_node
    from agents.bull_researcher import bull_researcher_node
    from agents.bear_researcher import bear_researcher_node
    from agents.trader import trader_node
    from agents.risk_manager import risk_manager_node
    from agents.fund_manager import fund_manager_node
    print("   OK: All 9 agents imported successfully")
except Exception as e:
    errors.append(str(e))
    print(f"   FAIL: {e}")

print("[2/5] Checking LangGraph wiring...")
try:
    from orchestrator.graph import trading_graph
    print("   OK: LangGraph compiled and all edges wired correctly")
except Exception as e:
    errors.append(str(e))
    print(f"   FAIL: {e}")

print("[3/5] Checking FastAPI routes...")
try:
    from api.main import app
    api_routes = [r.path for r in app.routes if hasattr(r, "path") and r.path.startswith("/api")]
    print(f"   OK: FastAPI loaded with {len(api_routes)} API routes")
    for r in api_routes:
        print(f"      - {r}")
except Exception as e:
    errors.append(str(e))
    print(f"   FAIL: {e}")

print("[4/5] Checking configuration (.env)...")
try:
    from config.settings import settings
    items = {
        "Groq API Key":    bool(settings.groq_api_key),
        "Groq Model":      settings.groq_model,
        "Dhan Client ID":  bool(settings.dhan_client_id),
        "Dhan Token":      bool(settings.dhan_access_token),
        "Exchange":        settings.default_exchange,
        "Currency":        settings.default_currency,
    }
    for k, v in items.items():
        status = "MISSING" if v is False else "OK"
        print(f"   {status}: {k} = {v}")
        if v is False:
            errors.append(f"Missing config: {k}")
except Exception as e:
    errors.append(str(e))
    print(f"   FAIL: {e}")

print("[5/5] Checking live market data (RELIANCE.NS via yfinance)...")
try:
    import yfinance as yf
    price = yf.Ticker("RELIANCE.NS").fast_info.last_price
    print(f"   OK: RELIANCE.NS current price = Rs {price:.2f}")
except Exception as e:
    errors.append(str(e))
    print(f"   FAIL: {e}")

print()
print("=" * 50)
if errors:
    print(f"RESULT: {len(errors)} issue(s) found:")
    for e in errors:
        print(f"  - {e}")
else:
    print("RESULT: ALL CHECKS PASSED")
    print("Run the backend:  python -m uvicorn api.main:app --reload --port 8000")
    print("Run the frontend: cd frontend && npm run dev")
print("=" * 50)
