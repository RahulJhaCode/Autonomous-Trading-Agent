# Autonomous Trading Agent

An AI-powered autonomous trading research and execution system for Indian markets. The project combines a multi-agent LangGraph workflow, Groq-hosted LLM reasoning, market data tools, broker integrations, a FastAPI backend, and a React dashboard for monitoring trading analysis in real time.

> Important: This project is for research, experimentation, and educational use. Trading in financial markets involves risk. Review every signal and order before using any real broker account.

## Overview

The system runs a complete trading analysis cycle for NSE/BSE stocks. It gathers market data, technical signals, news, sentiment, and fundamental context, then routes that information through multiple specialist agents before producing a trading decision. A risk manager checks the proposal before the fund manager layer can execute or simulate the final action.

## Key Features

- Multi-agent trading workflow built with LangGraph
- Groq LLM integration through LangChain
- Indian market configuration with INR, NSE/BSE defaults, and India market hours
- Fundamental, technical, sentiment, and news analysis agents
- Bull and bear researcher debate before trade proposal generation
- Risk gate with position sizing, confidence, volatility, and drawdown checks
- Optional broker integrations for Dhan and Shoonya/Finvasia
- FastAPI backend with REST endpoints and WebSocket support
- React + Vite dashboard with live trading status components
- Local memory support through ChromaDB
- Health check and diagnostic scripts for setup validation

## Architecture

```text
User / Dashboard
      |
      v
FastAPI Backend + WebSocket
      |
      v
LangGraph Orchestrator
      |
      +--> Fundamental Analyst
      +--> Technical Analyst
      +--> Sentiment Analyst
      +--> News Analyst
              |
              v
      Bull Researcher + Bear Researcher
              |
              v
            Trader
              |
              v
         Risk Manager
              |
              v
         Fund Manager
```

## Project Structure

```text
.
+-- agents/              # Specialist agent nodes for analysis, research, risk, and trading
+-- api/                 # FastAPI app, routes, and WebSocket manager
+-- config/              # Settings, LLM client, and Indian market configuration
+-- frontend/            # React + Vite dashboard
+-- memory/              # Vector memory integration
+-- orchestrator/        # LangGraph trading workflow and state models
+-- tests/               # Test package
+-- tools/               # Market data, news, search, and technical indicator tools
+-- health_check.py      # Full project health check
+-- diagnose_system.py   # Diagnostic script
+-- test_adaniports.py   # Example trading cycle test
+-- test_groq.py         # Groq connection test
+-- requirements.txt     # Python dependencies
+-- env.example.template # Example environment configuration
```

## Prerequisites

- Python 3.10 or newer
- Node.js 18 or newer
- npm
- Groq API key
- Optional: Dhan or Shoonya broker credentials
- Optional: Redis, if you want to use Redis-backed infrastructure

## Environment Setup

Create a local `.env` file from the template:

```powershell
copy env.example.template .env
```

Then update `.env` with your own values:

```env
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile
DHAN_CLIENT_ID=
DHAN_ACCESS_TOKEN=
```

Do not commit `.env`. The repository `.gitignore` is already configured to ignore environment files, local caches, Python bytecode, frontend dependencies, and ChromaDB persistence files.

## Backend Setup

Install Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Run the health check:

```powershell
python health_check.py
```

Start the API server:

```powershell
python -m uvicorn api.main:app --reload --port 8000
```

Useful backend URLs:

- API health: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`
- WebSocket: `ws://localhost:8000/ws`

## Frontend Setup

Install frontend dependencies:

```powershell
cd frontend
npm install
```

Start the dashboard:

```powershell
npm run dev
```

The Vite app usually runs at:

```text
http://localhost:5173
```

## Running a Trading Cycle

Run the orchestrator directly:

```powershell
python -m orchestrator.runner
```

The default example runs a trading cycle for `RELIANCE` on the `1D` timeframe. You can also call `run_trading_cycle()` from your own script:

```python
import asyncio
from orchestrator.runner import run_trading_cycle

asyncio.run(run_trading_cycle("ADANIPORTS", "1D"))
```

## Testing and Diagnostics

Check Groq connectivity:

```powershell
python test_groq.py
```

Run the project health check:

```powershell
python health_check.py
```

Run the example stock test:

```powershell
python test_adaniports.py
```

## GitHub Push Notes

Before pushing to GitHub, confirm that sensitive and generated files are ignored:

```powershell
git status --ignored
```

These should not be committed:

- `.env`
- `frontend/node_modules/`
- `__pycache__/`
- `memory/chroma_db/`
- log files

If this is a new repository:

```powershell
git init
git branch -M main
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/Autonomous_Trading_Agent.git
git push -u origin main
```

## Disclaimer

This software does not provide financial advice. It can generate incorrect analysis, incomplete signals, or risky trade proposals. Use paper trading or simulation first, and never deploy real capital without independent review, proper risk controls, and compliance with applicable laws and broker terms.
