from fastapi import APIRouter, BackgroundTasks
from typing import Optional, Literal, List, Dict
import requests
from ..services.data_fetcher import build_screener_data, run_full_screener_sync, get_cached_screener_data
from ..services.tracker import save_snapshot, detect_changes
from ..database.db import get_sync_status
from ..data.stock_universe import get_sectors as get_universe_sectors, STOCK_UNIVERSE, ALIASES
import asyncio

router = APIRouter(prefix="/api/screener", tags=["screener"])


@router.get("")
async def get_screener(
    exchange: Literal["NSE", "BSE", "BOTH"] = "NSE",
    min_rs: int = 0,
    max_rs: int = 99,
    above_ema200: bool = False,
    above_ema50: bool = False,
    min_price: float = 0.0,
    max_price: float = 999999,
    min_market_cap_cr: float = 0,
    min_turnover_cr: float = 0,
    max_from_52w_high_pct: float = 0,
    volume_surge: bool = False,
    sector: Optional[str] = None,
    limit: int = 500,
):
    """Main screener endpoint — serves pre-calculated metrics instantly from DB/cache."""
    results = await build_screener_data(
        exchange=exchange,
        min_rs=min_rs,
        max_rs=max_rs,
        above_ema200=above_ema200,
        above_ema50=above_ema50,
        min_price=min_price,
        max_price=max_price,
        min_market_cap=min_market_cap_cr * 1e7,
        min_turnover_cr=min_turnover_cr,
        max_from_52w_high_pct=max_from_52w_high_pct,
        volume_surge=volume_surge,
        sector=sector,
    )

    symbols = [r["symbol"] for r in results]
    filter_key = f"rs{min_rs}_{exchange}_{'ema200' if above_ema200 else 'all'}"
    asyncio.create_task(asyncio.to_thread(save_snapshot, symbols, filter_key))

    limit = min(limit, 1000)
    return {
        "total": len(results),
        "exchange": exchange,
        "data": results[:limit],
    }


@router.get("/sectors")
async def get_sectors_list(exchange: Literal["NSE", "BSE", "BOTH"] = "NSE"):
    """Get list of available sectors."""
    sectors = get_universe_sectors()
    return {"sectors": sectors}


@router.get("/status")
async def get_status():
    """Get system and sync status."""
    return get_sync_status()


@router.post("/sync")
async def trigger_sync(background_tasks: BackgroundTasks, exchange: str = "NSE"):
    """Manually trigger background sync."""
    background_tasks.add_task(run_full_screener_sync, exchange)
    return {"status": "started", "message": "Background sync triggered"}


@router.get("/search")
async def search_stocks(q: str = ""):
    """Unified stock search covering local pre-computed metrics and 5,000+ NSE, BSE & NSE:SME listed companies."""
    query = q.strip()
    if not query:
        return {"query": "", "results": []}

    query_upper = query.upper()
    results = []
    seen = set()

    # 1. Search cached screener metrics
    cached = get_cached_screener_data()
    for item in cached:
        sym = item.get("symbol", "").upper()
        name = item.get("name", "")
        if query_upper in sym or query.lower() in name.lower():
            if sym not in seen:
                seen.add(sym)
                results.append({
                    "symbol": sym,
                    "name": name,
                    "exchange": item.get("exchange", "BOTH"),
                    "sector": item.get("sector", ""),
                    "sub_industry": item.get("sub_industry", item.get("industry", "")),
                    "close": item.get("close", 0.0),
                    "rs_rating": item.get("rs_rating", 50),
                    "source": "local",
                })

    # 2. Check universe metadata
    for item in STOCK_UNIVERSE:
        sym = item.get("symbol", "").upper()
        name = item.get("name", "")
        if sym not in seen and (query_upper in sym or query.lower() in name.lower()):
            seen.add(sym)
            results.append({
                "symbol": sym,
                "name": name,
                "exchange": item.get("exchange", "BOTH"),
                "sector": item.get("sector", ""),
                "sub_industry": item.get("sub_industry", item.get("industry", "")),
                "close": 0.0,
                "rs_rating": 50,
                "source": "universe",
            })

    # 3. Check ALIASES (e.g. ZOMATO -> ETERNAL)
    if query_upper in ALIASES:
        target = ALIASES[query_upper]
        if target not in seen and target != query_upper:
            seen.add(target)
            results.insert(0, {
                "symbol": target,
                "name": f"{query_upper} (Renamed to {target})",
                "exchange": "BOTH",
                "sector": "Equity",
                "sub_industry": "",
                "close": 0.0,
                "rs_rating": 50,
                "source": "alias",
            })

    # 4. If fewer than 8 results and query length >= 2, search live Screener.in API
    # (covers all 5,000+ companies across NSE, BSE, and NSE:SME)
    if len(results) < 8 and len(query) >= 2:
        try:
            r = requests.get(
                f"https://www.screener.in/api/company/search/?q={query}",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=3,
            )
            if r.status_code == 200:
                for item in r.json():
                    url = item.get("url", "")
                    parts = [p for p in url.strip("/").split("/") if p and p != "company" and p != "consolidated"]
                    if parts:
                        sym = parts[0].upper()
                        if sym not in seen:
                            seen.add(sym)
                            name = item.get("name", sym)
                            exch = "BSE" if sym.isdigit() else "NSE"
                            results.append({
                                "symbol": sym,
                                "name": name,
                                "exchange": exch,
                                "sector": "NSE/BSE Listed",
                                "sub_industry": "SME / Equity",
                                "close": 0.0,
                                "rs_rating": 50,
                                "source": "online",
                            })
        except Exception:
            pass

    # Sort results: exact symbol match first, then prefix match, then others
    def sort_key(r):
        s = r["symbol"]
        if s == query_upper:
            return 0
        if s.startswith(query_upper):
            return 1
        if query.lower() in r["name"].lower():
            return 2
        return 3

    results.sort(key=sort_key)
    return {"query": query, "results": results[:10]}
