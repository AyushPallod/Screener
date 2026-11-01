"""
RS Rating Calculator — IBD-style Relative Strength Rating.

Formula (IBD-style):
  RS Score = (0.4 × Q4 return) + (0.2 × Q3 return) + (0.2 × Q2 return) + (0.2 × Q1 return)
  where Q4 is the most recent quarter, Q1 the oldest.
  
  RS Rating = Percentile rank of RS Score among all stocks in the universe (1-99).
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio


def calculate_rs_score(prices: pd.Series) -> float:
    """Calculate raw RS score from a price series."""
    if len(prices) < 20:
        return 0.0
    
    current = float(prices.iloc[-1])
    
    def safe_return(days_ago: int) -> float:
        idx = max(0, len(prices) - days_ago)
        past = float(prices.iloc[idx])
        if past == 0:
            return 0.0
        return (current - past) / past

    # Quarterly returns (~63 trading days per quarter)
    q4 = safe_return(63)    # most recent ~3 months
    q3 = safe_return(126)   # 3-6 months
    q2 = safe_return(189)   # 6-9 months
    q1 = safe_return(252)   # 9-12 months

    return (0.4 * q4) + (0.2 * q3) + (0.2 * q2) + (0.2 * q1)


def calculate_rs_ratings(universe: Dict[str, pd.Series]) -> Dict[str, Dict]:
    """
    Calculate RS Ratings for all stocks in universe.
    Returns dict of {symbol: {rs_rating, rs_3m, rs_6m, rs_12m}}
    """
    scores = {}
    returns_3m = {}
    returns_6m = {}
    returns_12m = {}

    for symbol, prices in universe.items():
        if len(prices) < 10:
            continue
        try:
            current = float(prices.iloc[-1])

            def ret(days: int) -> float:
                idx = max(0, len(prices) - days)
                past = float(prices.iloc[idx])
                return ((current - past) / past * 100) if past != 0 else 0.0

            scores[symbol] = calculate_rs_score(prices)
            returns_3m[symbol] = ret(63)
            returns_6m[symbol] = ret(126)
            returns_12m[symbol] = ret(252)
        except Exception:
            continue

    if not scores:
        return {}

    # Percentile rank → 1-99
    symbols = list(scores.keys())
    score_vals = np.array([scores[s] for s in symbols])
    r3m_vals = np.array([returns_3m.get(s, 0) for s in symbols])
    r6m_vals = np.array([returns_6m.get(s, 0) for s in symbols])
    r12m_vals = np.array([returns_12m.get(s, 0) for s in symbols])

    def percentile_rank(vals):
        ranks = {}
        n = len(vals)
        sorted_idx = np.argsort(vals)
        for rank_pos, arr_idx in enumerate(sorted_idx):
            pct = int(round((rank_pos / max(n - 1, 1)) * 98)) + 1  # 1-99
            ranks[symbols[arr_idx]] = min(99, max(1, pct))
        return ranks

    rs_ratings = percentile_rank(score_vals)
    rs_3m_ratings = percentile_rank(r3m_vals)
    rs_6m_ratings = percentile_rank(r6m_vals)
    rs_12m_ratings = percentile_rank(r12m_vals)

    return {
        symbol: {
            "rs_rating": rs_ratings.get(symbol, 50),
            "rs_3m": rs_3m_ratings.get(symbol, 50),
            "rs_6m": rs_6m_ratings.get(symbol, 50),
            "rs_12m": rs_12m_ratings.get(symbol, 50),
        }
        for symbol in symbols
    }


def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    """Calculate EMA for given period."""
    return prices.ewm(span=period, adjust=False).mean()


def is_above_ema(prices: pd.Series, period: int) -> bool:
    """Check if current price is above EMA."""
    if len(prices) < period:
        return False
    ema = calculate_ema(prices, period)
    return float(prices.iloc[-1]) > float(ema.iloc[-1])


def get_from_52w_high(prices: pd.Series, days: int = 252) -> float:
    """Get % below 52-week high (negative = below high)."""
    recent = prices.iloc[-min(days, len(prices)):]
    high = float(recent.max())
    current = float(prices.iloc[-1])
    if high == 0:
        return 0.0
    return ((current - high) / high) * 100


def detect_volume_surge(volumes: pd.Series, lookback: int = 20, threshold: float = 2.0) -> bool:
    """Detect if recent volume is significantly above average."""
    if len(volumes) < lookback + 1:
        return False
    avg_vol = float(volumes.iloc[-(lookback + 1):-1].mean())
    recent_vol = float(volumes.iloc[-1])
    if avg_vol == 0:
        return False
    return (recent_vol / avg_vol) >= threshold


def avg_daily_turnover(closes: pd.Series, volumes: pd.Series, days: int = 30) -> float:
    """Calculate average daily turnover in Crores."""
    if len(closes) < days or len(volumes) < days:
        return 0.0
    recent_closes = closes.iloc[-days:]
    recent_vols = volumes.iloc[-days:]
    turnover = (recent_closes * recent_vols).mean()
    return turnover / 1e7  # Convert to Crores
