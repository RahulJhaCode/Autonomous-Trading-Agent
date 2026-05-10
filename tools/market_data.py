"""
tools/market_data.py
────────────────────
Indian market data tool — fetches OHLCV, fundamentals, and real-time
quotes from Yahoo Finance using NSE (.NS) ticker format.

Key points for Indian markets:
  • yfinance uses SYMBOL.NS for NSE and SYMBOL.BO for BSE
  • India VIX: ^INDIAVIX  (equivalent of US VIX)
  • Nifty 50 index: ^NSEI
  • Sensex index:   ^BSESN
  • Market hours:   9:15 AM – 3:30 PM IST (UTC+5:30)
  • Currency:       INR (₹)
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import yfinance as yf
from loguru import logger

from config.settings import settings
from config.indian_markets import resolve_ticker, is_indian_ticker, get_stock


# ─────────────────────────────────────────────────────────────────
# Ticker Resolution
# ─────────────────────────────────────────────────────────────────

def normalise_ticker(ticker: str) -> str:
    """
    Ensure ticker has proper .NS suffix for Indian stocks.
    If ticker is already a full yfinance ticker (has a dot), return as-is.
    """
    ticker = ticker.strip().upper()
    if "." in ticker:
        return ticker   # Already has suffix (.NS, .BO, etc.)
    if ticker.startswith("^"):
        return ticker   # Index tickers (^NSEI, ^BSESN, ^INDIAVIX) — no suffix needed

    # Resolve via Indian market registry
    resolved, _ = resolve_ticker(ticker)
    return resolved


# ─────────────────────────────────────────────────────────────────
# OHLCV Data
# ─────────────────────────────────────────────────────────────────

async def get_ohlcv(ticker: str, period: str = "3mo", interval: str = "1d") -> pd.DataFrame:
    """
    Download OHLCV data asynchronously using yfinance.
    Automatically adds .NS suffix for Indian stocks.
    """
    yf_ticker = normalise_ticker(ticker)
    loop = asyncio.get_event_loop()
    df = await loop.run_in_executor(
        None,
        lambda: yf.download(yf_ticker, period=period, interval=interval, progress=False),
    )
    if df.empty:
        logger.warning(f"No OHLCV data returned for {yf_ticker}")
    else:
        logger.debug(f"Fetched {len(df)} rows of OHLCV data for {yf_ticker}")
    return df


# ─────────────────────────────────────────────────────────────────
# Real-time Price
# ─────────────────────────────────────────────────────────────────

async def get_current_price(ticker: str) -> float | None:
    """Fetch the latest market price for a ticker (in INR for Indian stocks)."""
    yf_ticker = normalise_ticker(ticker)
    loop = asyncio.get_event_loop()
    try:
        info = await loop.run_in_executor(
            None, lambda: yf.Ticker(yf_ticker).fast_info
        )
        price = float(info.last_price)
        logger.debug(f"Current price {yf_ticker}: ₹{price:,.2f}")
        return price
    except Exception as e:
        logger.error(f"Error fetching price for {yf_ticker}: {e}")
        return None


# ─────────────────────────────────────────────────────────────────
# Fundamentals
# ─────────────────────────────────────────────────────────────────

async def get_fundamentals(ticker: str) -> dict[str, Any]:
    """Return key fundamental metrics from yfinance for Indian stocks."""
    yf_ticker = normalise_ticker(ticker)
    loop = asyncio.get_event_loop()
    try:
        info = await loop.run_in_executor(
            None, lambda: yf.Ticker(yf_ticker).info
        )

        # Enrich with Indian market registry data
        stock_meta = get_stock(ticker)

        return {
            # Valuation
            "pe_ratio":             info.get("trailingPE"),
            "forward_pe":           info.get("forwardPE"),
            "price_to_book":        info.get("priceToBook"),
            "ev_to_ebitda":         info.get("enterpriseToEbitda"),
            # Earnings
            "eps":                  info.get("trailingEps"),
            "eps_forward":          info.get("forwardEps"),
            "revenue_growth":       info.get("revenueGrowth"),
            "earnings_growth":      info.get("earningsGrowth"),
            # Balance sheet
            "debt_to_equity":       info.get("debtToEquity"),
            "current_ratio":        info.get("currentRatio"),
            "return_on_equity":     info.get("returnOnEquity"),
            "return_on_assets":     info.get("returnOnAssets"),
            "profit_margins":       info.get("profitMargins"),
            "gross_margins":        info.get("grossMargins"),
            "free_cash_flow":       info.get("freeCashflow"),
            # Market data
            "market_cap":           info.get("marketCap"),
            "market_cap_cr":        _to_crore(info.get("marketCap")),   # In Crores (₹)
            "analyst_rating":       info.get("recommendationKey"),
            "target_price":         info.get("targetMeanPrice"),
            "52w_high":             info.get("fiftyTwoWeekHigh"),
            "52w_low":              info.get("fiftyTwoWeekLow"),
            "avg_volume":           info.get("averageVolume"),
            "dividend_yield":       info.get("dividendYield"),
            # Company info
            "short_name":           info.get("shortName", ticker),
            "sector":               stock_meta.sector if stock_meta else info.get("sector", "Unknown"),
            "industry":             info.get("industry", "Unknown"),
            "exchange":             "NSE",
            "currency":             "INR",
            # Index membership
            "nifty50":              stock_meta.nifty50 if stock_meta else False,
            "sensex30":             stock_meta.sensex30 if stock_meta else False,
        }
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {yf_ticker}: {e}")
        return {}


def _to_crore(value: float | None) -> str | None:
    """Convert INR value to Crores (1 Crore = 10 million)."""
    if value is None:
        return None
    crore = value / 1e7
    if crore >= 100_000:
        return f"₹{crore/1_00_000:.2f} Lakh Cr"
    return f"₹{crore:,.2f} Cr"


# ─────────────────────────────────────────────────────────────────
# India VIX (Fear Index)
# ─────────────────────────────────────────────────────────────────

async def get_india_vix() -> float:
    """
    Get the current India VIX value.
    India VIX < 15  → Very calm market
    India VIX 15-20 → Normal volatility
    India VIX > 20  → Elevated fear
    India VIX > 25  → High fear — reduce positions
    """
    price = await get_current_price("^INDIAVIX")
    vix_val = price or 15.0
    logger.info(f"India VIX: {vix_val:.2f}")
    return vix_val


# ─────────────────────────────────────────────────────────────────
# Index Prices
# ─────────────────────────────────────────────────────────────────

async def get_index_prices() -> dict[str, float | None]:
    """Fetch Nifty 50 and Sensex index levels."""
    tasks = [
        get_current_price("^NSEI"),    # Nifty 50
        get_current_price("^BSESN"),   # Sensex
        get_india_vix(),
    ]
    nifty, sensex, vix = await asyncio.gather(*tasks)
    return {
        "nifty_50": nifty,
        "sensex":   sensex,
        "india_vix": vix,
    }


# ─────────────────────────────────────────────────────────────────
# Market Session Check
# ─────────────────────────────────────────────────────────────────

def is_market_open() -> bool:
    """
    Check if NSE is currently open (9:15 AM – 3:30 PM IST, Mon–Fri).
    Note: Does not account for market holidays.
    """
    import pytz
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)

    if now_ist.weekday() >= 5:   # Saturday=5, Sunday=6
        return False

    open_time  = now_ist.replace(hour=9,  minute=15, second=0, microsecond=0)
    close_time = now_ist.replace(hour=15, minute=30, second=0, microsecond=0)
    return open_time <= now_ist <= close_time
