"""
api/websocket_manager.py
────────────────────────
Manages WebSocket connections and broadcasts real-time agent
updates to all connected dashboard clients.
"""
from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket
from loguru import logger


class WebSocketManager:
    """Tracks all active WebSocket connections and broadcasts messages."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, data: dict[str, Any]) -> None:
        """Send a JSON message to all connected clients."""
        message = json.dumps(data)
        dead_connections = []
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except Exception:
                dead_connections.append(conn)
        # Clean up dead connections
        for dead in dead_connections:
            self.disconnect(dead)

    async def send_agent_event(self, agent: str, status: str, data: Any = None) -> None:
        """Helper to broadcast a structured agent lifecycle event."""
        await self.broadcast({
            "type":   "agent_event",
            "agent":  agent,
            "status": status,   # running | completed | error
            "data":   data,
        })

    async def send_trade_alert(self, ticker: str, action: str, details: dict) -> None:
        """Broadcast a trade execution alert."""
        await self.broadcast({
            "type":    "trade_alert",
            "ticker":  ticker,
            "action":  action,
            "details": details,
        })


# Singleton instance
ws_manager = WebSocketManager()
