"""
agents/risk_manager.py — Indian market edition (Azure OpenAI).
Uses India VIX instead of US VIX. Sizes in INR.
"""
from __future__ import annotations

import re
from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from config.llm_client import get_chat_llm
from config.settings import settings
from orchestrator.state import TradingState, RiskAssessment
from tools.market_data import get_india_vix

SYSTEM_PROMPT = """You are the Chief Risk Officer (CRO) at an Indian equity hedge fund.

Indian market specific risk rules:
- SEBI regulations prohibit circular trading and front-running
- F&O positions require margin — ensure adequate capital
- Stocks in ASM/GSM lists have higher volatility risk — avoid
- Illiquid stocks (< ₹5 Cr daily turnover) should be avoided
- Max single-day move allowed by SEBI: 20% (upper/lower circuit)
- India VIX > 20 = elevated risk; > 25 = suspend new positions
- Currency risk: ₹/$ movements affect export/import sensitive stocks

Check ALL of the following:
1. Confidence score above threshold?
2. Position size within portfolio concentration limit (INR)?
3. India VIX acceptable?
4. Risk/reward ratio > 2:1 minimum?
5. Stop loss defined?

Output EXACTLY:
APPROVED: [YES | NO]
CONFIDENCE_CHECK: [PASS | FAIL]
POSITION_SIZE_CHECK: [PASS | FAIL]
MARKET_CONDITIONS_CHECK: [PASS | FAIL]
RISK_REWARD_CHECK: [PASS | FAIL]
ADJUSTED_POSITION_INR: [number or UNCHANGED]
REJECTION_REASONS: [comma-separated or NONE]
CRO_NOTES: [1-2 sentences]
"""


def _run_hard_rules(state: TradingState, india_vix: float) -> list[str]:
    """Hard-coded guardrails — cannot be overridden by LLM."""
    reasons = []
    tp = state.trade_proposal
    conf = state.confidence_score

    if conf < settings.min_confidence_score:
        reasons.append(f"Confidence {conf:.0%} < minimum {settings.min_confidence_score:.0%}")

    if tp and tp.position_size_usd > 0:
        max_allowed = state.portfolio_value * (settings.max_position_size_pct / 100)
        if tp.position_size_usd > max_allowed:
            reasons.append(f"Position ₹{tp.position_size_usd:,.0f} > max ₹{max_allowed:,.0f}")

    if india_vix > settings.max_volatility_indiavix:
        reasons.append(f"India VIX {india_vix:.1f} > threshold {settings.max_volatility_indiavix}")

    if tp and tp.action in ("BUY", "SELL") and tp.stop_loss is None:
        reasons.append("No stop loss defined — mandatory for all non-HOLD positions")

    return reasons


async def risk_manager_node(state: TradingState) -> dict:
    """LangGraph node: Risk Manager Agent for Indian markets."""
    ticker = state.ticker
    logger.info(f"[RiskManager] Validating trade for {ticker}...")

    llm = get_chat_llm(temperature=0.0, max_tokens=512)

    try:
        india_vix = await get_india_vix()
        hard_failures = _run_hard_rules(state, india_vix)

        tp = state.trade_proposal
        human_msg = f"""TRADE PROPOSAL (Indian NSE Market):
Ticker: {ticker}
Action: {tp.action if tp else 'N/A'}
Position Size: ₹{f'{tp.position_size_usd:,.2f}' if tp else '0'} INR
Entry Price: ₹{tp.entry_price or 'MARKET'}
Take Profit: ₹{tp.take_profit or 'N/A'}
Stop Loss: ₹{tp.stop_loss or 'N/A'}
Confidence Score: {state.confidence_score:.0%}
Rationale: {tp.rationale if tp else 'N/A'}

MARKET CONDITIONS:
India VIX: {india_vix:.2f} (threshold: {settings.max_volatility_indiavix})
Portfolio Value: ₹{state.portfolio_value:,.2f}
Max Position Size: ₹{state.portfolio_value * settings.max_position_size_pct / 100:,.0f} ({settings.max_position_size_pct}%)

HARD RULE VIOLATIONS:
{chr(10).join(f"  {r}" for r in hard_failures) if hard_failures else " None detected"}

Evaluate this NSE trade proposal and provide your risk assessment."""

        messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=human_msg)]
        response = await llm.ainvoke(messages)
        text = response.content

        def extract(pattern, default=""):
            m = re.search(pattern, text, re.IGNORECASE)
            return m.group(1).strip() if m else default

        approved_str = extract(r"APPROVED:\s*(YES|NO)", "NO")
        approved = (approved_str.upper() == "YES") and len(hard_failures) == 0

        adj_str = extract(r"ADJUSTED_POSITION_INR:\s*([\d,.]+|UNCHANGED)", "UNCHANGED")
        adj_size = None
        if adj_str != "UNCHANGED":
            try:
                adj_size = float(adj_str.replace(",", ""))
            except ValueError:
                pass

        rejection_str = extract(r"REJECTION_REASONS:\s*(.+)", "NONE")
        llm_reasons = [] if rejection_str.upper() == "NONE" else [r.strip() for r in rejection_str.split(",")]
        all_reasons = hard_failures + llm_reasons

        assessment = RiskAssessment(
            approved=approved,
            confidence_check="PASS" in extract(r"CONFIDENCE_CHECK:\s*(PASS|FAIL)", "FAIL"),
            position_size_check="PASS" in extract(r"POSITION_SIZE_CHECK:\s*(PASS|FAIL)", "FAIL"),
            drawdown_check="PASS" in extract(r"MARKET_CONDITIONS_CHECK:\s*(PASS|FAIL)", "FAIL"),
            liquidity_check=True,
            rejection_reasons=all_reasons,
            adjusted_position_size_usd=adj_size,
        )

        status = "APPROVED" if approved else "REJECTED"
        logger.log("SUCCESS" if approved else "WARNING",
                   f"[RiskManager] {status} — {ticker} | Violations: {all_reasons or 'None'}")

        return {
            "risk_assessment": assessment,
            "agent_logs": [f"RiskManager: {status} for {ticker}"],
        }

    except Exception as e:
        logger.error(f"[RiskManager] Error: {e}")
        return {
            "risk_assessment": RiskAssessment(approved=False, rejection_reasons=[f"Error: {e}"]),
            "errors": [f"RiskManager error: {e}"],
        }
