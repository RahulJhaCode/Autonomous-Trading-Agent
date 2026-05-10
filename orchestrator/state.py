"""
orchestrator/state.py
─────────────────────
Shared TradingState Pydantic model — the single source of truth
that flows through every LangGraph node.
"""
from __future__ import annotations

from typing import Annotated, Any, Literal, Optional
from pydantic import BaseModel, Field
import operator


# ─── Sub-models ───────────────────────────────────────────────────────────────

class FundamentalReport(BaseModel):
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    revenue_growth_yoy: Optional[float] = None
    debt_to_equity: Optional[float] = None
    free_cash_flow: Optional[float] = None
    analyst_rating: Optional[str] = None
    summary: str = ""


class TechnicalSignals(BaseModel):
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    trend: Optional[Literal["BULLISH", "BEARISH", "NEUTRAL"]] = None
    summary: str = ""


class NewsEvent(BaseModel):
    headline: str
    source: str
    sentiment: Literal["POSITIVE", "NEGATIVE", "NEUTRAL"]
    relevance_score: float = 0.0
    published_at: str = ""


class TradeProposal(BaseModel):
    action: Literal["BUY", "SELL", "HOLD"] = "HOLD"
    position_size_usd: float = 0.0
    entry_price: Optional[float] = None
    take_profit: Optional[float] = None
    stop_loss: Optional[float] = None
    rationale: str = ""


class RiskAssessment(BaseModel):
    approved: bool = False
    confidence_check: bool = False
    position_size_check: bool = False
    drawdown_check: bool = False
    liquidity_check: bool = False
    rejection_reasons: list[str] = Field(default_factory=list)
    adjusted_position_size_usd: Optional[float] = None


class ExecutionResult(BaseModel):
    order_id: Optional[str] = None
    status: Optional[str] = None
    filled_price: Optional[float] = None
    filled_qty: Optional[float] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


# ─── Main State ───────────────────────────────────────────────────────────────

class TradingState(BaseModel):
    """
    Shared state that flows through every node in the LangGraph.
    Annotated fields with operator.add allow concurrent nodes to
    append to lists without overwriting each other.
    """

    # ── Input ──────────────────────────────────────────────────────
    ticker: str = ""
    timeframe: str = "1D"
    current_price: Optional[float] = None
    portfolio_value: float = 100_000.0   # Starting paper capital

    # ── Analyst Outputs (populated concurrently) ───────────────────
    fundamental_report: Optional[FundamentalReport] = None
    sentiment_score: Optional[float] = None          # -1.0 (bearish) → +1.0 (bullish)
    sentiment_summary: str = ""
    technical_signals: Optional[TechnicalSignals] = None
    news_events: Annotated[list[NewsEvent], operator.add] = Field(default_factory=list)

    # ── Research Layer ─────────────────────────────────────────────
    bull_argument: str = ""
    bear_argument: str = ""
    research_summary: str = ""
    confidence_score: float = 0.0   # 0.0 → 1.0

    # ── Trader Decision ────────────────────────────────────────────
    trade_proposal: Optional[TradeProposal] = None

    # ── Risk Assessment ────────────────────────────────────────────
    risk_assessment: Optional[RiskAssessment] = None

    # ── Fund Manager ───────────────────────────────────────────────
    final_approved: bool = False
    fund_manager_notes: str = ""

    # ── Execution ──────────────────────────────────────────────────
    execution_result: Optional[ExecutionResult] = None

    # ── Logging / Debug ────────────────────────────────────────────
    agent_logs: Annotated[list[str], operator.add] = Field(default_factory=list)
    errors: Annotated[list[str], operator.add] = Field(default_factory=list)
