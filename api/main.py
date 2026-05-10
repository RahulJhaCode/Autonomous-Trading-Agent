"""
api/main.py
───────────
FastAPI application entry point.
Exposes REST endpoints + WebSocket for real-time dashboard updates.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.routes import dashboard, trades, control
from api.websocket_manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("Autonomous Trading Agent API starting...")
    yield
    logger.info("Shutting down API...")


app = FastAPI(
    title="Autonomous Trading Agent",
    description="Multi-agent LLM-powered autonomous trading system",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(trades.router,    prefix="/api/trades",    tags=["Trades"])
app.include_router(control.router,   prefix="/api/control",   tags=["Control"])


# ── WebSocket Endpoint ────────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time WebSocket endpoint for dashboard live updates."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; updates are pushed from agent pipeline
            data = await websocket.receive_text()
            await ws_manager.broadcast({"type": "echo", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "autonomous-trading-agent"}


if __name__ == "__main__":
    import uvicorn
    from config.settings import settings
    uvicorn.run("api.main:app", host=settings.api_host, port=settings.api_port, reload=True)
