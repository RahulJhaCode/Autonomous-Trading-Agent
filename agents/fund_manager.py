"""
agents/fund_manager.py — Indian market edition (Groq LLM).
Final approver and executor. Places orders via Dhan API (free).
"""
from __future__ import annotations

import re
from datetime import datetime
from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm_client import get_chat_llm
from config.indian_markets import get_stock
from config.settings import settings
from orchestrator.state import TradingState, ExecutionResult

SYSTEM_PROMPT = """You are the Fund Manager (CIO) at an elite Indian equity hedge fund trading on NSE/BSE.

Final review before trade execution. Consider:
1. Does this trade align with the overall portfolio strategy?
2. Is timing optimal — avoid placing orders in first 15 mins (9:15–9:30) and last 10 mins (3:20–3:30) of NSE session
3. Check if there are any pending corporate actions (dividends, splits) that affect timing
4. Verify the stock isn't currently in a circuit filter (locked limit up/down)
5. Confirm position size is sensible relative to stock's daily liquidity

All amounts in INR (₹). You have final absolute veto authority.

Output:
FINAL_DECISION: [EXECUTE | VETO | WAIT]
NOTES: [2-3 sentences]
"""


async def _place_zerodha_order(
    ticker: str, action: str, qty: int, entry_price: float | None
) -> ExecutionResult:
    """Place order via Zerodha Kite Connect API."""
    if not settings.dhan_client_id and not settings.shoonya_user_id:
        logger.warning("[FundManager] Zerodha not configured — simulating paper order")
        return ExecutionResult(
            order_id=f"PAPER-NSE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="simulated",
            filled_price=entry_price or 0.0,
            filled_qty=float(qty),
            timestamp=datetime.now().isoformat(),
        )

    try:
        from kiteconnect import KiteConnect
        kite = KiteConnect(api_key=settings.zerodha_api_key)
        kite.set_access_token(settings.zerodha_access_token)

        order_id = kite.place_order(
            tradingsymbol=ticker,
            exchange=kite.EXCHANGE_NSE,
            transaction_type=kite.TRANSACTION_TYPE_BUY if action == "BUY" else kite.TRANSACTION_TYPE_SELL,
            quantity=qty,
            product=kite.PRODUCT_CNC,        # Delivery (CNC) for equity
            order_type=kite.ORDER_TYPE_MARKET,
            variety=kite.VARIETY_REGULAR,
        )
        logger.success(f"Zerodha order placed: {order_id}")
        return ExecutionResult(
            order_id=str(order_id),
            status="placed",
            filled_price=entry_price,
            filled_qty=float(qty),
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"Zerodha order error: {e}")
        return ExecutionResult(error=str(e), status="failed")


async def _place_shoonya_order(
    ticker: str, action: str, qty: int, entry_price: float | None
) -> ExecutionResult:
    """Place order via Shoonya (Finvasia) — FREE API."""
    if not settings.shoonya_user_id or not settings.shoonya_password:
        logger.warning("[FundManager] Shoonya not configured — simulating order")
        return ExecutionResult(
            order_id=f"PAPER-SHOONYA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="simulated",
            filled_price=entry_price or 0.0,
            filled_qty=float(qty),
            timestamp=datetime.now().isoformat(),
        )

    try:
        from NorenRestApiPy.NorenApi import NorenApi
        api = NorenApi()
        
        # Login
        ret = api.login(
            userid=settings.shoonya_user_id,
            password=settings.shoonya_password,
            twoFA='123456', # This needs to be handled via TOTP in production
            vendor_code=settings.shoonya_vendor_code,
            api_secret=settings.shoonya_api_key,
            imei=settings.shoonya_imei
        )

        if ret['stat'] != 'Ok':
            raise Exception(f"Shoonya Login Failed: {ret['emsg']}")

        # Place Order
        res = api.place_order(
            buy_or_sell='B' if action == "BUY" else 'S',
            product_type='C', # Cash
            exchange='NSE',
            tradingsymbol=ticker.replace(".NS", ""),
            quantity=qty,
            discloseqty=0,
            price_type='MKT', # Market
            price=0,
            trigger_price=0,
            retention='DAY',
            remarks='AI_Bot_Trade'
        )

        if res['stat'] == 'Ok':
            return ExecutionResult(
                order_id=res['norenordno'],
                status="placed",
                filled_price=entry_price,
                filled_qty=float(qty),
                timestamp=datetime.now().isoformat(),
            )
        else:
            raise Exception(res['emsg'])

    except Exception as e:
        logger.error(f"Shoonya order error: {e}")
        return ExecutionResult(error=str(e), status="failed")


async def _place_dhan_order(
    ticker: str, action: str, qty: int, entry_price: float | None
) -> ExecutionResult:
    """Place order via Dhan (DhanHQ) — FREE API."""
    if not settings.dhan_client_id or not settings.dhan_access_token:
        logger.warning("[FundManager] Dhan not configured — simulating order")
        return ExecutionResult(
            order_id=f"PAPER-DHAN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            status="simulated",
            filled_price=entry_price or 0.0,
            filled_qty=float(qty),
            timestamp=datetime.now().isoformat(),
        )

    try:
        from dhanhq import dhanhq, DhanContext
        
        # New pattern for DhanHQ v2.2+
        context = DhanContext(settings.dhan_client_id, settings.dhan_access_token)
        dhan = dhanhq(context)
        
        # Dhan order placement
        # Exchange: 1=NSE, 2=BSE
        # Transaction Type: 1=BUY, 2=SELL
        # Order Type: 1=MARKET, 2=LIMIT
        res = dhan.place_order(
            security_id=ticker.replace(".NS", ""), # Requires mapping to Dhan security ID in production
            exchange_segment='NSE_EQ',
            transaction_type='BUY' if action == "BUY" else 'SELL',
            quantity=qty,
            order_type='MARKET',
            product_type='CNC', # Delivery
            price=0
        )

        if res['status'] == 'success':
            return ExecutionResult(
                order_id=str(res['data']['orderId']),
                status="placed",
                filled_price=entry_price,
                filled_qty=float(qty),
                timestamp=datetime.now().isoformat(),
            )
        else:
            raise Exception(res['remarks'])

    except Exception as e:
        logger.error(f"Dhan order error: {e}")
        return ExecutionResult(error=str(e), status="failed")


async def fund_manager_node(state: TradingState) -> dict:
    """LangGraph node: Fund Manager — final approver and executor."""
    ticker = state.ticker
    stock_meta = get_stock(ticker)
    logger.info(f"[FundManager] Final review for {ticker}...")

    llm = get_chat_llm(temperature=0.0, max_tokens=400)

    try:
        tp = state.trade_proposal
        ra = state.risk_assessment

        human_msg = f"""TRADE DOSSIER — {ticker} ({stock_meta.name if stock_meta else ''}) on NSE

TRADE PROPOSAL:
  Action: {tp.action if tp else 'N/A'}
  Position Size: ₹{f'{tp.position_size_usd:,.2f}' if tp else '0'} INR
  Entry: ₹{tp.entry_price or 'MARKET'}
  Take Profit: ₹{tp.take_profit or 'N/A'}
  Stop Loss: ₹{tp.stop_loss or 'N/A'}
  Rationale: {tp.rationale if tp else 'N/A'}

CONFIDENCE: {state.confidence_score:.0%}
RISK STATUS: {'APPROVED' if ra and ra.approved else 'REJECTED'}
ADJUSTED SIZE: ₹{f'{ra.adjusted_position_size_usd:,.2f}' if ra and ra.adjusted_position_size_usd else 'UNCHANGED'}

RESEARCH SUMMARY:
{state.research_summary[:500] if state.research_summary else 'N/A'}

As Indian equity Fund Manager, do you approve final NSE execution?"""

        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=human_msg)]
        response = await llm.ainvoke(messages)
        text = response.content

        decision_m = re.search(r"FINAL_DECISION:\s*(EXECUTE|VETO|WAIT)", text, re.IGNORECASE)
        decision = decision_m.group(1).upper() if decision_m else "VETO"
        notes_m = re.search(r"NOTES:\s*(.+)", text, re.DOTALL)
        notes = notes_m.group(1).strip()[:300] if notes_m else text[:300]

        final_approved = (decision == "EXECUTE")
        execution_result = None

        if final_approved and tp and tp.action in ("BUY", "SELL"):
            size = ra.adjusted_position_size_usd if (ra and ra.adjusted_position_size_usd) else tp.position_size_usd
            price = state.current_price or 1.0
            qty = max(1, int(size // price))   # Whole shares only (NSE rule)

            # Choose broker: Prefer Dhan (Free for User) -> Shoonya (Free) -> Zerodha
            if settings.dhan_client_id:
                execution_result = await _place_dhan_order(ticker, tp.action, qty, tp.entry_price)
            elif settings.shoonya_user_id:
                execution_result = await _place_shoonya_order(ticker, tp.action, qty, tp.entry_price)
            else:
                execution_result = await _place_zerodha_order(ticker, tp.action, qty, tp.entry_price)
            
            logger.success(
                f"[FundManager] 🎯 ORDER — {tp.action} {qty} shares of {ticker} "
                f"| Order ID: {execution_result.order_id}"
            )
        else:
            logger.info(f"[FundManager] {decision} — {ticker}: {notes[:100]}")

        return {
            "final_approved":     final_approved,
            "fund_manager_notes": notes,
            "execution_result":   execution_result,
            "agent_logs":         [f"FundManager: {decision} — {ticker}"],
        }

    except Exception as e:
        logger.error(f"[FundManager] Error: {e}")
        return {
            "final_approved":     False,
            "fund_manager_notes": f"Error: {e}",
            "errors":             [f"FundManager error: {e}"],
        }
