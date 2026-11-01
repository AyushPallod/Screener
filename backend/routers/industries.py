from fastapi import APIRouter
from typing import Literal, Optional
from ..services.data_fetcher import get_sector_performance, get_sector_stocks_performance

router = APIRouter(prefix="/api/industries", tags=["industries"])

PERIOD_MAP = {
    "today": 1,
    "1w": 5,
    "1m": 21,
    "3m": 63,
    "6m": 126,
    "ytd": 250,
    "1y": 252,
}


@router.get("")
async def get_industries(
    exchange: Literal["NSE", "BSE", "BOTH"] = "NSE",
    period: Literal["today", "1w", "1m", "3m", "6m", "ytd", "1y"] = "1w",
    group_by: Literal["sector", "industry", "sub_industry"] = "sector",
    screener_only: bool = False,
    min_rs: int = 0,
):
    """
    Get sector/industry/sub-industry performance aggregated from pre-calculated metrics.
    When screener_only=True, rankings are evaluated solely across stocks passing screener criteria.
    """
    days = PERIOD_MAP.get(period, 5)
    data = await get_sector_performance(
        exchange=exchange,
        period_days=days,
        group_by=group_by,
        screener_only=screener_only,
        min_rs=min_rs,
    )
    return {
        "period": period,
        "group_by": group_by,
        "screener_only": screener_only,
        "exchange": exchange,
        "data": data,
    }


@router.get("/{sector_name}/stocks")
async def get_sector_stocks(
    sector_name: str,
    exchange: Literal["NSE", "BSE", "BOTH"] = "NSE",
    period: Literal["today", "1w", "1m", "3m", "6m", "ytd", "1y"] = "1w",
    group_by: Literal["sector", "industry", "sub_industry"] = "sector",
    screener_only: bool = False,
    min_rs: int = 0,
    above_ema200: bool = False,
):
    """
    Get stocks within a sector/industry/sub-industry directly from the screener data.
    Only screener stocks are returned, pre-sorted by screener RS rating.
    """
    days = PERIOD_MAP.get(period, 5)
    stocks = await get_sector_stocks_performance(
        sector_name=sector_name,
        exchange=exchange,
        period_days=days,
        group_by=group_by,
        screener_only=screener_only,
        min_rs=min_rs,
        above_ema200_only=above_ema200,
    )
    return {
        "sector": sector_name,
        "period": period,
        "group_by": group_by,
        "screener_only": screener_only,
        "exchange": exchange,
        "stocks": stocks,
    }
