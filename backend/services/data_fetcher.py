"""
Data Fetcher — primary data layer with startup pre-calculation and database persistence.
Downloads stock data in controlled, throttled chunks with automatic retries.
All screener and industry queries read directly from cached / persistent store for instant responses.
"""

import asyncio
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import yfinance as yf

from ..database.db import (
    save_screener_metrics, load_all_screener_metrics,
    save_daily_prices, get_daily_candles,
    set_sync_status, get_sync_status
)
from ..data.stock_universe import (
    get_all_symbols, get_meta, get_sectors, get_stocks_in_sector
)
from .rs_calculator import (
    calculate_rs_ratings, calculate_rs_score,
    is_above_ema, get_from_52w_high, detect_volume_surge, avg_daily_turnover
)
from .tracker import save_snapshot

# ── In-Memory Fast Cache ───────────────────────────────────────────────────────
_lock = threading.Lock()
_screener_cache: List[Dict] = []
_price_cache: Dict[str, pd.DataFrame] = {}
_is_syncing: bool = False


def load_screener_from_db():
    """Load pre-calculated metrics from SQLite into memory on server startup."""
    global _screener_cache
    with _lock:
        rows = load_all_screener_metrics("BOTH")
        if rows:
            _screener_cache = rows
            print(f"[DataFetcher] Loaded {len(rows)} stocks from database cache.")
        else:
            print("[DataFetcher] No previous cache in database. Initial sync needed.")


def get_cached_screener_data() -> List[Dict]:
    """Get active in-memory screener data, loading from DB if empty."""
    global _screener_cache
    with _lock:
        if not _screener_cache:
            rows = load_all_screener_metrics("BOTH")
            if rows:
                _screener_cache = rows
        return list(_screener_cache)


# ── yfinance Chunked Downloader with Retry ─────────────────────────────────────

def _download_chunk(tickers: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
    """Download a chunk of tickers synchronously without bursting threads."""
    if not tickers:
        return {}
    try:
        raw = yf.download(
            tickers,
            period=period,
            group_by="ticker",
            auto_adjust=True,
            progress=False,
            threads=False,
        )
        result = {}
        if raw.empty:
            return result

        is_multi = isinstance(raw.columns, pd.MultiIndex)

        for sym in tickers:
            try:
                if is_multi:
                    if sym in raw.columns.levels[0]:
                        sub = raw[sym].dropna(subset=["Close"])
                        if not sub.empty and len(sub) >= 1:
                            result[sym] = sub
                else:
                    if "Close" in raw.columns:
                        sub = raw.dropna(subset=["Close"])
                        if not sub.empty and len(sub) >= 1:
                            result[sym] = sub
            except Exception:
                pass
        return result
    except Exception as e:
        print(f"[yfinance] Chunk download error: {e}")
        return {}


def _retry_failed_tickers(failed_tickers: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
    """Retry failed tickers individually or in small batches of 3 with a short backoff and SME fallback."""
    if not failed_tickers:
        return {}
    print(f"[yfinance] Retrying {len(failed_tickers)} failed tickers...")
    recovered = {}
    for sym in failed_tickers:
        time.sleep(0.3)
        try:
            t = yf.Ticker(sym)
            df = t.history(period=period, auto_adjust=True)
            if not df.empty and len(df) >= 2:
                recovered[sym] = df
            elif sym.endswith(".NS") and not sym.endswith("-SM.NS"):
                sme_sym = sym.replace(".NS", "-SM.NS")
                t_sme = yf.Ticker(sme_sym)
                df_sme = t_sme.history(period=period, auto_adjust=True)
                if not df_sme.empty and len(df_sme) >= 2:
                    recovered[sym] = df_sme
        except Exception:
            pass
    print(f"[yfinance] Recovered {len(recovered)} / {len(failed_tickers)} tickers on retry.")
    return recovered


def download_all_universe_stocks(stocks: List[Dict], period: str = "1y", chunk_size: int = 35) -> Dict[str, pd.DataFrame]:
    """
    Download historical price data for the entire stock universe in controlled chunks.
    Maps yfinance ticker results back to canonical stock symbols.
    """
    # Build mapping from yf_symbol to canonical symbol
    yf_to_sym = {s["yf_symbol"]: s["symbol"] for s in stocks}
    all_yf_tickers = list(yf_to_sym.keys())
    total_tickers = len(all_yf_tickers)

    print(f"[Sync] Starting batch download for {total_tickers} stocks in chunks of {chunk_size}...")
    set_sync_status("syncing", "5%", total_tickers, 0, f"Downloading 0/{total_tickers} stocks...")

    price_map: Dict[str, pd.DataFrame] = {}
    failed_yf: List[str] = []

    # Download in chunks sequentially to respect Yahoo rate limits
    for i in range(0, total_tickers, chunk_size):
        chunk = all_yf_tickers[i:i + chunk_size]
        chunk_res = _download_chunk(chunk, period)

        for yf_sym in chunk:
            if yf_sym in chunk_res and not chunk_res[yf_sym].empty:
                base_sym = yf_to_sym[yf_sym]
                price_map[base_sym] = chunk_res[yf_sym]
            else:
                failed_yf.append(yf_sym)

        processed = min(i + chunk_size, total_tickers)
        pct = int((processed / total_tickers) * 75)
        set_sync_status("syncing", f"{pct}%", total_tickers, processed, f"Downloaded {processed}/{total_tickers} stocks...")
        time.sleep(0.5)

    # Retry any dropped tickers
    if failed_yf:
        recovered = _retry_failed_tickers(failed_yf, period)
        for yf_sym, df in recovered.items():
            base_sym = yf_to_sym[yf_sym]
            price_map[base_sym] = df

    print(f"[Sync] Finished downloading. Successfully retrieved data for {len(price_map)} / {total_tickers} stocks.")
    return price_map


# ── Metric Calculation ─────────────────────────────────────────────────────────

def calculate_metrics_for_universe(price_map: Dict[str, pd.DataFrame], stocks: List[Dict]) -> List[Dict]:
    """Compute RS Ratings, EMAs, 52W high %, turnover, and period returns for all stocks."""
    if not price_map:
        return []

    close_series: Dict[str, pd.Series] = {sym: df["Close"] for sym, df in price_map.items() if not df.empty}
    rs_data = calculate_rs_ratings(close_series)

    stock_meta_map = {s["symbol"]: s for s in stocks}
    results = []

    for sym, df in price_map.items():
        if df.empty or len(df) < 5:
            continue

        prices = df["Close"]
        vols = df["Volume"] if "Volume" in df.columns else pd.Series(dtype=float)
        meta = stock_meta_map.get(sym, get_meta(sym))

        close = float(prices.iloc[-1])
        prev_close = float(prices.iloc[-2]) if len(prices) >= 2 else close

        def safe_ret(days_ago: int) -> float:
            if len(prices) <= days_ago:
                past = float(prices.iloc[0])
            else:
                past = float(prices.iloc[-(days_ago + 1)])
            return round(((close - past) / past * 100), 2) if past > 0 else 0.0

        rs = rs_data.get(sym, {"rs_rating": 50, "rs_3m": 50, "rs_6m": 50, "rs_12m": 50})
        from52h = get_from_52w_high(prices)
        turnover = avg_daily_turnover(prices, vols) if len(vols) > 0 else 0.0
        vol_surge = detect_volume_surge(vols) if len(vols) > 0 else False
        rs_raw = calculate_rs_score(prices)

        results.append({
            "symbol": sym,
            "name": meta.get("name", sym),
            "exchange": meta.get("exchange", "NSE"),
            "sector": meta.get("sector", "Other"),
            "industry": meta.get("industry", "Other"),
            "sub_industry": meta.get("sub_industry", meta.get("industry", "Other")),
            "close": round(close, 2),
            "prev_close": round(prev_close, 2),
            "market_cap": 0.0,
            "pe": None,
            "rs_rating": int(rs["rs_rating"]),
            "rs_3m": int(rs["rs_3m"]),
            "rs_6m": int(rs["rs_6m"]),
            "rs_12m": int(rs["rs_12m"]),
            "rs_score_raw": round(rs_raw, 4),
            "from_52w_high": round(from52h, 1),
            "above_ema50": 1 if is_above_ema(prices, 50) else 0,
            "above_ema200": 1 if is_above_ema(prices, 200) else 0,
            "avg_turnover_cr": round(turnover, 1),
            "volume_surge": 1 if vol_surge else 0,
            "return_1d": round(((close - prev_close) / prev_close * 100), 2) if prev_close > 0 else 0.0,
            "return_1w": safe_ret(5),
            "return_1m": safe_ret(21),
            "return_3m": safe_ret(63),
            "return_6m": safe_ret(126),
            "return_1y": safe_ret(252),
        })

    results.sort(key=lambda x: x["rs_rating"], reverse=True)
    return results


# ── Full Sync Runner ───────────────────────────────────────────────────────────

async def run_full_screener_sync(exchange: str = "NSE") -> Dict:
    """Run full background sync: download price data, compute metrics, and persist to SQLite."""
    global _screener_cache, _price_cache, _is_syncing

    if _is_syncing:
        return {"status": "already_syncing"}

    _is_syncing = True
    try:
        stocks = get_all_symbols(exchange if exchange != "BOTH" else "NSE")
        if exchange == "BOTH":
            stocks += get_all_symbols("BSE")

        # Run heavy download in thread pool to avoid blocking FastAPI event loop
        loop = asyncio.get_event_loop()
        price_map = await loop.run_in_executor(None, download_all_universe_stocks, stocks, "1y", 35)

        if not price_map:
            set_sync_status("error", "0%", len(stocks), 0, "No price data downloaded")
            return {"status": "error", "message": "Failed to download prices"}

        set_sync_status("syncing", "80%", len(stocks), len(price_map), "Calculating technical metrics & RS ratings...")

        # Calculate metrics
        metrics = calculate_metrics_for_universe(price_map, stocks)

        # Persist to SQLite
        set_sync_status("syncing", "90%", len(stocks), len(metrics), "Storing metrics in database...")
        save_screener_metrics(metrics)
        save_daily_prices(price_map)

        # Update in-memory caches
        with _lock:
            _screener_cache = metrics
            _price_cache = price_map

        # Record screener snapshot for entry/exit tracker
        top_symbols = [m["symbol"] for m in metrics if m["rs_rating"] >= 80 and m["above_ema200"]]
        filter_key = f"rs80_{exchange}_ema200"
        save_snapshot(top_symbols, filter_key)

        set_sync_status("completed", "100%", len(stocks), len(metrics), f"Successfully synced {len(metrics)} stocks")
        print(f"[Sync] Completed! {len(metrics)} stocks stored and ready.")
        return {"status": "completed", "stocks_synced": len(metrics)}
    except Exception as e:
        print(f"[Sync] Error during sync: {e}")
        set_sync_status("error", "0%", 0, 0, f"Error: {str(e)}")
        return {"status": "error", "error": str(e)}
    finally:
        _is_syncing = False


def is_matching_exchange(stock_exchange: str, requested_exchange: str) -> bool:
    """Check if stock exchange matches requested exchange filter."""
    if requested_exchange == "BOTH":
        return True
    if stock_exchange == "BOTH":
        return True
    return stock_exchange.upper() == requested_exchange.upper()


# ── Public APIs (Served from Cache / DB with 0 latency) ────────────────────────

async def build_screener_data(
    exchange: str = "NSE",
    min_rs: int = 0,
    max_rs: int = 99,
    above_ema200: bool = False,
    above_ema50: bool = False,
    min_price: float = 0,
    max_price: float = 999999,
    min_market_cap: float = 0,
    min_turnover_cr: float = 0,
    max_from_52w_high_pct: float = 0,
    volume_surge: bool = False,
    sector: Optional[str] = None,
) -> List[Dict]:
    """
    Main screener query — executes in milliseconds directly against the pre-calculated store.
    Supports NSE, BSE, and BOTH exchanges.
    """
    data = get_cached_screener_data()
    if not data:
        data = load_all_screener_metrics(exchange)

    results = []
    for r in data:
        if not is_matching_exchange(r.get("exchange", "BOTH"), exchange):
            continue
        if not (min_rs <= r.get("rs_rating", 0) <= max_rs):
            continue
        close = r.get("close", 0)
        if close < min_price or close > max_price:
            continue
        if above_ema200 and not r.get("above_ema200"):
            continue
        if above_ema50 and not r.get("above_ema50"):
            continue
        if max_from_52w_high_pct < 0 and r.get("from_52w_high", 0) < max_from_52w_high_pct:
            continue
        if min_turnover_cr > 0 and r.get("avg_turnover_cr", 0) < min_turnover_cr:
            continue
        if volume_surge and not r.get("volume_surge"):
            continue
        if min_market_cap > 0 and r.get("market_cap", 0) < min_market_cap:
            continue
        if sector and sector.lower() not in (r.get("sector") or "").lower():
            continue

        item = dict(r)
        if exchange in ("NSE", "BSE"):
            item["exchange"] = exchange
        results.append(item)

    results.sort(key=lambda x: x.get("rs_rating", 0), reverse=True)
    return results


async def get_sector_performance(
    exchange: str = "NSE",
    period_days: int = 5,
    group_by: str = "sector",
    screener_only: bool = False,
    min_rs: int = 0,
    above_ema200_only: bool = False,
) -> List[Dict]:
    """
    Get sector/industry/sub-industry performance aggregated from pre-computed metrics.
    When screener_only=True, calculates rankings exclusively for stocks that passed the screener.
    """
    data = get_cached_screener_data()
    if not data:
        data = load_all_screener_metrics(exchange)

    # Determine which precomputed return field to use
    ret_field = "return_1w"
    if period_days <= 1:
        ret_field = "return_1d"
    elif period_days <= 7:
        ret_field = "return_1w"
    elif period_days <= 30:
        ret_field = "return_1m"
    elif period_days <= 90:
        ret_field = "return_3m"
    elif period_days <= 180:
        ret_field = "return_6m"
    else:
        ret_field = "return_1y"

    group_dict: Dict[str, List[Dict]] = {}
    for r in data:
        if not is_matching_exchange(r.get("exchange", "BOTH"), exchange):
            continue

        # If screener_only is enabled, consider only stocks passing screener criteria
        if screener_only:
            thresh = min_rs if min_rs > 0 else 80
            if r.get("rs_rating", 0) < thresh or not r.get("above_ema200"):
                continue
        elif min_rs > 0 and r.get("rs_rating", 0) < min_rs:
            continue

        if above_ema200_only and not r.get("above_ema200"):
            continue

        # Determine grouping key based on group_by
        if group_by == "industry":
            key = r.get("industry") or "Other"
        elif group_by == "sub_industry":
            key = r.get("sub_industry") or r.get("industry") or "Other"
        else:
            key = r.get("sector") or "Other"

        group_dict.setdefault(key, []).append(r)

    result = []
    for grp_name, stocks in group_dict.items():
        total = len(stocks)
        if total == 0:
            continue
        returns = [s.get(ret_field, 0.0) for s in stocks]
        above_ema = sum(1 for s in stocks if s.get("above_ema200"))
        advancing = sum(1 for ret in returns if ret > 0)
        declining = sum(1 for ret in returns if ret < 0)
        avg_ret = float(np.mean(returns)) if returns else 0.0

        result.append({
            "sector": grp_name,
            "group_type": group_by,
            "total_stocks": total,
            "advancing": advancing,
            "declining": declining,
            "avg_return_pct": round(avg_ret, 2),
            "above_ema200_count": above_ema,
            "breadth": f"{above_ema}/{total}",
            "screener_only": screener_only,
        })

    result.sort(key=lambda x: x["avg_return_pct"], reverse=True)
    return result


async def get_sector_stocks_performance(
    sector_name: str,
    exchange: str = "NSE",
    period_days: int = 5,
    group_by: str = "sector",
    screener_only: bool = False,
    min_rs: int = 0,
    above_ema200_only: bool = False,
) -> List[Dict]:
    """
    Get stocks within a sector/industry directly from the screener dataset.
    Stocks are sorted by screener RS rating / performance so they match the screener.
    """
    data = get_cached_screener_data()
    if not data:
        data = load_all_screener_metrics(exchange)

    ret_field = "return_1w"
    if period_days <= 1:
        ret_field = "return_1d"
    elif period_days <= 7:
        ret_field = "return_1w"
    elif period_days <= 30:
        ret_field = "return_1m"
    elif period_days <= 90:
        ret_field = "return_3m"
    elif period_days <= 180:
        ret_field = "return_6m"
    else:
        ret_field = "return_1y"

    target_name = sector_name.lower().strip()
    results = []

    for r in data:
        if not is_matching_exchange(r.get("exchange", "BOTH"), exchange):
            continue

        # Match against target based on group_by
        if group_by == "industry":
            field_val = (r.get("industry") or "").lower()
            if target_name != field_val and target_name not in field_val:
                continue
        elif group_by == "sub_industry":
            field_val = (r.get("sub_industry") or "").lower()
            if target_name != field_val and target_name not in field_val:
                continue
        else:
            field_val = (r.get("sector") or "").lower()
            if target_name != field_val and target_name not in field_val and target_name not in (r.get("industry") or "").lower():
                continue

        if screener_only:
            thresh = min_rs if min_rs > 0 else 80
            if r.get("rs_rating", 0) < thresh or not r.get("above_ema200"):
                continue
        elif min_rs > 0 and r.get("rs_rating", 0) < min_rs:
            continue

        if above_ema200_only and not r.get("above_ema200"):
            continue

        results.append({
            "symbol": r["symbol"],
            "name": r.get("name", r["symbol"]),
            "exchange": exchange if exchange in ("NSE", "BSE") else r.get("exchange", "NSE"),
            "sector": r.get("sector", ""),
            "industry": r.get("industry", ""),
            "sub_industry": r.get("sub_industry", ""),
            "close": r.get("close", 0.0),
            "period_return": r.get(ret_field, 0.0),
            "rs_score": r.get("rs_rating", 50),
            "above_ema200": bool(r.get("above_ema200")),
            "market_cap": r.get("market_cap", 0),
        })

    # Sorted by screener RS rating descending (matching the screener!)
    results.sort(key=lambda x: (x["rs_score"], x["period_return"]), reverse=True)
    return results


async def fetch_historical_prices(symbol: str, exchange: str = "NSE", days: int = 380) -> pd.DataFrame:
    """Fetch historical OHLCV. Checks in-memory cache, then SQLite daily_prices, then yfinance."""
    sym = symbol.upper().replace(".NS", "").replace(".BO", "")

    # Check in-memory price cache
    with _lock:
        if sym in _price_cache and not _price_cache[sym].empty:
            return _price_cache[sym]

    # Check SQLite daily_prices table
    candles = get_daily_candles(sym, days)
    if candles:
        df = pd.DataFrame(candles)
        df["Date"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("Date", inplace=True)
        df.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}, inplace=True)
        return df[["Open", "High", "Low", "Close", "Volume"]]

    # Fallback to single yfinance download
    meta = get_meta(sym)
    yf_sym = meta.get("yf_symbol", f"{sym}.NS")
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, _download_chunk, [yf_sym], "1y" if days <= 380 else "2y")
    df = res.get(yf_sym, pd.DataFrame())

    # Fallback for NSE SME stocks if symbol.NS didn't return data
    if df.empty and yf_sym.endswith(".NS") and not yf_sym.endswith("-SM.NS"):
        sme_sym = yf_sym.replace(".NS", "-SM.NS")
        res = await loop.run_in_executor(None, _download_chunk, [sme_sym], "1y" if days <= 380 else "2y")
        df = res.get(sme_sym, pd.DataFrame())

    # Fallback for BSE stocks if requested exchange is BSE or ticker exists on BSE
    if df.empty and (exchange == "BSE" or not yf_sym.endswith(".BO")):
        bse_sym = f"{sym}.BO"
        res = await loop.run_in_executor(None, _download_chunk, [bse_sym], "1y" if days <= 380 else "2y")
        df = res.get(bse_sym, pd.DataFrame())

    if not df.empty:
        save_daily_prices({sym: df})
        with _lock:
            _price_cache[sym] = df
    return df


async def fetch_stock_universe(exchange: str = "NSE") -> List[Dict]:
    """Return stock universe metadata."""
    return get_all_symbols(exchange if exchange != "BOTH" else "NSE") + \
           (get_all_symbols("BSE") if exchange == "BOTH" else [])
