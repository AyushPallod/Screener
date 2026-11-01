from fastapi import APIRouter
from typing import Literal
import pandas as pd
from ..services.data_fetcher import fetch_historical_prices, get_cached_screener_data
from ..services.rs_calculator import calculate_rs_score, is_above_ema, get_from_52w_high
from ..services.financial_service import get_company_financials, get_company_shareholding, get_company_ratios
from ..database.db import get_daily_candles
from ..data.stock_universe import get_meta

router = APIRouter(prefix="/api/company", tags=["company"])


@router.get("/{symbol}/ohlcv")
async def get_ohlcv(
    symbol: str,
    exchange: Literal["NSE", "BSE"] = "NSE",
    days: int = 365,
):
    """Get OHLCV candlestick data for TradingView charts. Uses SQLite cache first for instant loads."""
    sym = symbol.upper()

    # Fast path: retrieve from SQLite pre-computed daily_prices
    candles = get_daily_candles(sym, days)
    if candles:
        return {"symbol": sym, "exchange": exchange, "candles": candles}

    # Fallback to fetch_historical_prices
    df = await fetch_historical_prices(sym, exchange, days)
    if df.empty:
        return {"symbol": sym, "exchange": exchange, "candles": []}

    candles = []
    for ts, row in df.iterrows():
        try:
            t = int(ts.timestamp()) if hasattr(ts, 'timestamp') else int(pd.Timestamp(ts).timestamp())
            candles.append({
                "time": t,
                "open": round(float(row.get("Open", row.get("Close", 0))), 2),
                "high": round(float(row.get("High", row.get("Close", 0))), 2),
                "low": round(float(row.get("Low", row.get("Close", 0))), 2),
                "close": round(float(row.get("Close", 0)), 2),
                "volume": int(float(row.get("Volume", 0) or 0)),
            })
        except Exception:
            continue

    return {"symbol": sym, "exchange": exchange, "candles": candles}


@router.get("/{symbol}")
async def get_company_detail(
    symbol: str,
    exchange: Literal["NSE", "BSE"] = "NSE",
):
    """Get detailed company information from screener store."""
    sym = symbol.upper()
    cached = get_cached_screener_data()
    item = next((r for r in cached if r["symbol"].upper() == sym), None)

    # Fetch/extract key ratios (Market Cap, PE, 52W High/Low, Book Value, etc.)
    ratios = get_company_ratios(sym)
    mcap = (item.get("market_cap") if item and item.get("market_cap") else None) or ratios.get("market_cap") or 0.0
    pe = item.get("pe") if (item and item.get("pe") is not None) else ratios.get("pe")
    w52_high = ratios.get("52w_high")
    w52_low = ratios.get("52w_low")

    if w52_high is None or w52_low is None:
        candles = get_daily_candles(sym, 365)
        if candles:
            if w52_high is None:
                w52_high = round(max(c["high"] for c in candles), 2)
            if w52_low is None:
                w52_low = round(min(c["low"] for c in candles), 2)

    if item:
        return {
            "symbol": sym,
            "name": item.get("name", sym),
            "exchange": item.get("exchange", exchange),
            "sector": item.get("sector", ""),
            "industry": item.get("industry", ""),
            "sub_industry": item.get("sub_industry", ""),
            "close": item.get("close", 0.0),
            "market_cap": mcap,
            "pe": pe,
            "52w_high": w52_high,
            "52w_low": w52_low,
            "book_value": ratios.get("book_value"),
            "dividend_yield": ratios.get("dividend_yield"),
            "roce": ratios.get("roce"),
            "roe": ratios.get("roe"),
            "rs_rating": item.get("rs_rating", 50),
            "from_52w_high": item.get("from_52w_high", 0.0),
            "above_ema50": bool(item.get("above_ema50")),
            "above_ema200": bool(item.get("above_ema200")),
            "avg_turnover_cr": item.get("avg_turnover_cr", 0.0),
            "volume_surge": bool(item.get("volume_surge")),
            "return_1d": item.get("return_1d", 0.0),
            "return_1w": item.get("return_1w", 0.0),
            "return_1m": item.get("return_1m", 0.0),
            "return_3m": item.get("return_3m", 0.0),
            "return_6m": item.get("return_6m", 0.0),
            "return_1y": item.get("return_1y", 0.0),
            "rs_score_raw": item.get("rs_score_raw", 0.0),
            "tradingview_symbol": f"{exchange}:{sym}",
        }

    # Fallback if not found in cache
    df = await fetch_historical_prices(sym, exchange)
    if df.empty:
        return {"error": f"No data found for {sym}"}

    prices = df["Close"]
    current = float(prices.iloc[-1])

    def safe_ret(days: int) -> float:
        idx = max(0, len(prices) - days)
        past = float(prices.iloc[idx])
        return round(((current - past) / past * 100), 2) if past > 0 else 0.0

    rs_score = calculate_rs_score(prices)
    meta = get_meta(sym)

    return {
        "symbol": sym,
        "name": meta.get("name", sym),
        "exchange": exchange,
        "sector": meta.get("sector", ""),
        "industry": meta.get("industry", ""),
        "close": round(current, 2),
        "market_cap": mcap,
        "pe": pe,
        "52w_high": w52_high,
        "52w_low": w52_low,
        "book_value": ratios.get("book_value"),
        "dividend_yield": ratios.get("dividend_yield"),
        "roce": ratios.get("roce"),
        "roe": ratios.get("roe"),
        "rs_rating": 50,
        "from_52w_high": round(get_from_52w_high(prices), 1),
        "above_ema50": is_above_ema(prices, 50),
        "above_ema200": is_above_ema(prices, 200),
        "return_1d": safe_ret(1),
        "return_1w": safe_ret(5),
        "return_1m": safe_ret(21),
        "return_3m": safe_ret(63),
        "return_6m": safe_ret(126),
        "return_1y": safe_ret(252),
        "rs_score_raw": round(rs_score, 4),
        "tradingview_symbol": f"{exchange}:{sym}",
    }


@router.get("/{symbol}/financials")
async def get_financials(symbol: str, force_refresh: bool = False):
    """Get quarterly financial results (Sales, Expenses, Operating Profit, OPM%, PAT, EPS, etc.)."""
    return get_company_financials(symbol, force_refresh=force_refresh)


@router.get("/{symbol}/shareholding")
async def get_shareholding(symbol: str, force_refresh: bool = False):
    """Get shareholding pattern breakdown (Promoters, FIIs, DIIs, Public, Government)."""
    return get_company_shareholding(symbol, force_refresh=force_refresh)
