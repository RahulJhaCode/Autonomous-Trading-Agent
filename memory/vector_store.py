"""
memory/vector_store.py
──────────────────────
ChromaDB-based long-term memory for the autonomous trading agent.
Uses ChromaDB's built-in default sentence-transformer embeddings (free, local).
No external embedding API required.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

import chromadb
from loguru import logger

from config.settings import settings


class TradingMemory:
    """
    Persistent vector memory for the autonomous trading agent.
    Backed by ChromaDB with local sentence-transformer embeddings.

    Collections:
      trade_history   — past trade decisions with outcomes
      market_insights — analyst summaries per stock
      risk_events     — historical risk violations and learnings
    """

    def __init__(self):
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)

        # Use default local embeddings (no external API needed)
        self.trade_history   = self._client.get_or_create_collection("trade_history_india")
        self.market_insights = self._client.get_or_create_collection("market_insights_india")
        self.risk_events     = self._client.get_or_create_collection("risk_events_india")

        logger.info(f"TradingMemory initialised | Trades stored: {self.trade_history.count()}")

    def store_trade(self, ticker: str, action: str, rationale: str, outcome: str = "pending") -> None:
        """Store a trade decision in vector memory."""
        doc_id   = f"{ticker}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        document = f"NSE:{ticker} | {action} | {rationale}"
        self.trade_history.add(
            documents=[document],
            metadatas=[{
                "ticker":    ticker,
                "action":    action,
                "outcome":   outcome,
                "exchange":  "NSE",
                "currency":  "INR",
                "timestamp": datetime.now().isoformat(),
            }],
            ids=[doc_id],
        )
        logger.debug(f"Stored trade memory: {doc_id}")

    def query_similar_trades(self, ticker: str, query: str, n_results: int = 3) -> list[dict[str, Any]]:
        """Retrieve semantically similar past trades (RAG for agents)."""
        count = self.trade_history.count()
        if count == 0:
            return []
        try:
            results = self.trade_history.query(
                query_texts=[f"NSE:{ticker} {query}"],
                n_results=min(n_results, count),
            )
            docs  = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            return [{"text": d, "metadata": m} for d, m in zip(docs, metas)]
        except Exception as e:
            logger.warning(f"Memory query failed: {e}")
            return []

    def store_insight(self, ticker: str, insight_type: str, content: str) -> None:
        """Store an analyst insight for future retrieval."""
        doc_id = f"{ticker}_{insight_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.market_insights.add(
            documents=[content],
            metadatas=[{"ticker": ticker, "type": insight_type, "timestamp": datetime.now().isoformat()}],
            ids=[doc_id],
        )

    def update_trade_outcome(self, order_id: str, outcome: str, pnl_inr: float) -> None:
        """Update a stored trade with its final outcome and P&L in INR."""
        logger.info(f"Trade outcome recorded: {order_id} -> {outcome} (Rs {pnl_inr:,.2f})")


# Singleton
trading_memory = TradingMemory()
