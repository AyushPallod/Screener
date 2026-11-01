from fastapi import APIRouter
from ..services.tracker import (
    detect_changes, get_symbol_history,
    get_all_snapshots_summary, get_recent_movers
)

router = APIRouter(prefix="/api/tracker", tags=["tracker"])


@router.get("/changes")
async def get_changes(filter_key: str = "rs80_NSE_ema200"):
    """Get today's entry/exit changes."""
    return detect_changes(filter_key)


@router.get("/history/{symbol}")
async def get_history(symbol: str, filter_key: str = "rs80_NSE_ema200"):
    """Get entry/exit history for a specific symbol."""
    history = get_symbol_history(symbol.upper(), filter_key)
    return {"symbol": symbol.upper(), "filter_key": filter_key, "history": history}


@router.get("/snapshots")
async def get_snapshots(filter_key: str = "rs80_NSE_ema200"):
    """Get summary of all daily snapshots."""
    return {"snapshots": get_all_snapshots_summary(filter_key)}


@router.get("/movers")
async def get_movers(filter_key: str = "rs80_NSE_ema200", days: int = 7):
    """Get stocks that moved in/out in the last N days."""
    return get_recent_movers(filter_key, days)
