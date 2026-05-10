from dhanhq import dhanhq
from config.settings import settings
from config.llm_client import get_chat_llm
from tools.free_search import search_indian_markets
import asyncio
import sys

async def run_tests():
    print("--- STARTING SYSTEM DIAGNOSTICS ---\n")

    # 1. Test Dhan
    print("1. Testing Dhan Connection...")
    try:
        from dhanhq import dhanhq, DhanContext
        context = DhanContext(settings.dhan_client_id, settings.dhan_access_token)
        d = dhanhq(context)
        funds = d.get_fund_limits()
        if funds.get('status') == 'success':
            bal = funds.get('data', {}).get('availabelBalance', '0.0')
            print(f"DONE: Dhan SUCCESS (Available Balance: Rs {bal})")
        else:
            print(f"FAIL: Dhan FAILED ({funds.get('remarks', 'Unknown error')})")
    except Exception as e:
        print(f"ERROR: Dhan ERROR ({e})")

    # 2. Test Azure OpenAI
    print("\n2. Testing Azure OpenAI (Chat)...")
    try:
        llm = get_chat_llm()
        res = llm.invoke("Identify yourself and say 'Namaste, I am ready' in one sentence.")
        print(f"DONE: Azure SUCCESS ({res.content.strip()})")
    except Exception as e:
        print(f"ERROR: Azure ERROR ({e})")

    # 3. Test Free Search (DuckDuckGo)
    print("\n3. Testing Free News Search (DuckDuckGo)...")
    try:
        results = await search_indian_markets("Nifty 50 latest news", max_results=2)
        if results:
            print(f"DONE: Free Search SUCCESS (Found {len(results)} latest headlines)")
            for r in results:
                print(f"   - {r['title'][:60]}...")
        else:
            print("WARN: Free Search No results found (Check internet connection)")
    except Exception as e:
        print(f"ERROR: Free Search ERROR ({e})")

    print("\n--- DIAGNOSTICS COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_tests())
