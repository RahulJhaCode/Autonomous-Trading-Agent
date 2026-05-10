"""
tools/technical_indicators.py
──────────────────────────────
Compute technical indicators using pandas-ta on OHLCV DataFrames.
"""
from __future__ import annotations

import pandas as pd
import pandas_ta as ta
from loguru import logger

from orchestrator.state import TechnicalSignals


def compute_indicators(df: pd.DataFrame) -> TechnicalSignals:
    """
    Compute a comprehensive set of technical indicators.
    Returns a TechnicalSignals model.
    """
    if df.empty or len(df) < 20:
        logger.warning("Insufficient data to compute indicators")
        return TechnicalSignals(summary="Insufficient data for technical analysis.")

    try:
        close = df["Close"].squeeze()
        high  = df["High"].squeeze()
        low   = df["Low"].squeeze()

        # RSI (14)
        rsi = ta.rsi(close, length=14)
        rsi_val = float(rsi.iloc[-1]) if rsi is not None and not rsi.empty else None

        # MACD (12, 26, 9)
        macd_df = ta.macd(close, fast=12, slow=26, signal=9)
        macd_val   = float(macd_df["MACD_12_26_9"].iloc[-1])   if macd_df is not None else None
        signal_val = float(macd_df["MACDs_12_26_9"].iloc[-1])  if macd_df is not None else None

        # Bollinger Bands (20, 2)
        # pandas-ta v0.4.x uses doubled std suffix: BBU_20_2.0_2.0 instead of BBU_20_2.0
        bb = ta.bbands(close, length=20, std=2)
        bb_upper = None
        bb_lower = None
        if bb is not None:
            # Dynamically find the correct column names (handles both old and new naming)
            bbu_cols = [c for c in bb.columns if c.startswith("BBU_")]
            bbl_cols = [c for c in bb.columns if c.startswith("BBL_")]
            if bbu_cols:
                bb_upper = float(bb[bbu_cols[0]].iloc[-1])
            if bbl_cols:
                bb_lower = float(bb[bbl_cols[0]].iloc[-1])

        # SMAs
        sma50  = ta.sma(close, length=50)
        sma200 = ta.sma(close, length=200)
        sma50_val  = float(sma50.iloc[-1])  if sma50  is not None and not sma50.empty  else None
        sma200_val = float(sma200.iloc[-1]) if sma200 is not None and not sma200.empty else None

        # Trend determination
        current_price = float(close.iloc[-1])
        trend = _determine_trend(current_price, sma50_val, sma200_val, rsi_val, macd_val, signal_val)

        summary = _build_summary(ticker="", rsi=rsi_val, macd=macd_val, trend=trend,
                                  current_price=current_price, sma50=sma50_val)

        return TechnicalSignals(
            rsi_14=rsi_val,
            macd=macd_val,
            macd_signal=signal_val,
            bb_upper=bb_upper,
            bb_lower=bb_lower,
            sma_50=sma50_val,
            sma_200=sma200_val,
            trend=trend,
            summary=summary,
        )
    except Exception as e:
        logger.error(f"Error computing indicators: {e}")
        return TechnicalSignals(summary=f"Error during technical analysis: {e}")


def _determine_trend(price: float, sma50, sma200, rsi, macd, macd_signal) -> str:
    """Simple trend classification based on indicators."""
    bullish_signals = 0
    bearish_signals = 0

    if sma50 and price > sma50:    bullish_signals += 1
    elif sma50:                     bearish_signals += 1
    if sma200 and price > sma200:  bullish_signals += 1
    elif sma200:                    bearish_signals += 1
    if rsi and rsi > 50:           bullish_signals += 1
    elif rsi:                       bearish_signals += 1
    if macd and macd_signal and macd > macd_signal: bullish_signals += 1
    elif macd and macd_signal:                       bearish_signals += 1

    if bullish_signals >= 3:   return "BULLISH"
    elif bearish_signals >= 3: return "BEARISH"
    return "NEUTRAL"


def _build_summary(ticker: str, rsi, macd, trend: str, current_price: float, sma50) -> str:
    lines = [
        f"Price: ₹{current_price:.2f}",
        f"RSI(14): {rsi:.1f}" if rsi else "RSI: N/A",
        f"MACD: {macd:.3f}" if macd else "MACD: N/A",
        f"SMA50: ₹{sma50:.2f}" if sma50 else "SMA50: N/A",
        f"Overall Trend: {trend}",
    ]
    return " | ".join(lines)
