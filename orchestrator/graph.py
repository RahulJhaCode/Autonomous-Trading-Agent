"""
orchestrator/graph.py
─────────────────────
LangGraph StateGraph — wires all 9 agents into a concurrent,
hierarchical pipeline. Analyst agents run in PARALLEL (Superstep 1),
then the system converges through Research → Trader → Risk → Fund Manager.

Compatible with LangGraph v1.x (uses Command + Send for fan-out).
"""
from __future__ import annotations

from langgraph.graph import StateGraph, END
from langgraph.types import Command, Send

from orchestrator.state import TradingState

# ── Import all agent node functions ──────────────────────────────────────────
from agents.fundamental_analyst import fundamental_analyst_node
from agents.sentiment_analyst import sentiment_analyst_node
from agents.technical_analyst import technical_analyst_node
from agents.news_analyst import news_analyst_node
from agents.bull_researcher import bull_researcher_node
from agents.bear_researcher import bear_researcher_node
from agents.trader import trader_node
from agents.risk_manager import risk_manager_node
from agents.fund_manager import fund_manager_node


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator Entry Node — fans out to all 4 analysts CONCURRENTLY
# ─────────────────────────────────────────────────────────────────────────────

def orchestrator_node(state: TradingState) -> Command:
    """
    Uses LangGraph Command + Send to dispatch all 4 analyst agents
    in the same superstep (parallel execution). Each agent receives
    the full state.
    """
    return Command(
        goto=[
            Send("fundamental_analyst", state),
            Send("sentiment_analyst",   state),
            Send("technical_analyst",   state),
            Send("news_analyst",        state),
        ]
    )


# ─────────────────────────────────────────────────────────────────────────────
# Research Merge Node — waits for all 4 analysts, then runs Bull vs Bear
# ─────────────────────────────────────────────────────────────────────────────

def research_dispatcher_node(state: TradingState) -> Command:
    """Dispatch Bull and Bear researchers in parallel."""
    return Command(
        goto=[
            Send("bull_researcher", state),
            Send("bear_researcher", state),
        ]
    )


# ─────────────────────────────────────────────────────────────────────────────
# Risk Gate — routes to Fund Manager only if risk approved, else END
# ─────────────────────────────────────────────────────────────────────────────

def risk_gate(state: TradingState) -> str:
    """Conditional edge: only proceed if risk manager approved the trade."""
    if state.risk_assessment and state.risk_assessment.approved:
        return "fund_manager"
    return END


# ─────────────────────────────────────────────────────────────────────────────
# Build & Compile the Graph
# ─────────────────────────────────────────────────────────────────────────────

def build_trading_graph() -> StateGraph:
    graph = StateGraph(TradingState)

    # ── Register all nodes ────────────────────────────────────────
    graph.add_node("orchestrator",        orchestrator_node)
    graph.add_node("fundamental_analyst", fundamental_analyst_node)
    graph.add_node("sentiment_analyst",   sentiment_analyst_node)
    graph.add_node("technical_analyst",   technical_analyst_node)
    graph.add_node("news_analyst",        news_analyst_node)
    graph.add_node("research_dispatcher", research_dispatcher_node)
    graph.add_node("bull_researcher",     bull_researcher_node)
    graph.add_node("bear_researcher",     bear_researcher_node)
    graph.add_node("trader",              trader_node)
    graph.add_node("risk_manager",        risk_manager_node)
    graph.add_node("fund_manager",        fund_manager_node)

    # ── Define edges ──────────────────────────────────────────────
    # Entry point → parallel analyst fan-out
    graph.set_entry_point("orchestrator")

    # All 4 analysts → research dispatcher (LangGraph waits for all)
    graph.add_edge("fundamental_analyst", "research_dispatcher")
    graph.add_edge("sentiment_analyst",   "research_dispatcher")
    graph.add_edge("technical_analyst",   "research_dispatcher")
    graph.add_edge("news_analyst",        "research_dispatcher")

    # Research dispatcher → parallel Bull & Bear debate
    # Bull & Bear → Trader (LangGraph waits for both)
    graph.add_edge("bull_researcher", "trader")
    graph.add_edge("bear_researcher", "trader")

    # Trader → Risk Manager
    graph.add_edge("trader", "risk_manager")

    # Risk Manager → conditional: Fund Manager (approved) or END (rejected)
    graph.add_conditional_edges(
        "risk_manager",
        risk_gate,
        {"fund_manager": "fund_manager", END: END},
    )

    # Fund Manager → END
    graph.add_edge("fund_manager", END)

    return graph.compile()


# Compiled graph (importable singleton)
trading_graph = build_trading_graph()
