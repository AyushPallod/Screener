"""
BSE Data Client — fetches data from BSE India APIs.
"""

import httpx
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime

BSE_BASE = "https://api.bseindia.com/BseIndiaAPI/api"
BSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.bseindia.com/",
    "Origin": "https://www.bseindia.com",
}


class BSEClient:
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=BSE_HEADERS,
                timeout=30,
                follow_redirects=True,
            )
        return self._client

    async def _get(self, url: str) -> Optional[dict]:
        try:
            client = await self._get_client()
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[BSE] GET {url} failed: {e}")
        return None

    async def get_stock_quote(self, scripcode: str) -> Optional[Dict]:
        """Get BSE stock quote by scrip code."""
        url = f"{BSE_BASE}/getScripHeaderData/w?Debtflag=&scrip_cd={scripcode}&seriesid="
        data = await self._get(url)
        if data:
            return {
                "symbol": data.get("ShortName", scripcode),
                "name": data.get("LongName", ""),
                "exchange": "BSE",
                "close": float(data.get("CurrRate", 0) or 0),
                "change_pct": float(data.get("Prcntchng", 0) or 0),
                "market_cap": float(data.get("Mktcap", 0) or 0),
                "pe": data.get("PERatio"),
                "52w_high": float(data.get("High52Week", 0) or 0),
                "52w_low": float(data.get("Low52Week", 0) or 0),
                "volume": float(data.get("TotalTradedQuantity", 0) or 0),
            }
        return None

    async def get_bse500_stocks(self) -> List[Dict]:
        """Get BSE 500 component list."""
        url = f"{BSE_BASE}/GetIndexData/w?index=16&type=D"
        data = await self._get(url)
        if data and "Table" in data:
            return [
                {
                    "symbol": row.get("scrip_cd", ""),
                    "name": row.get("scrip_name", ""),
                    "exchange": "BSE",
                    "sector": row.get("INDUSTRY", ""),
                    "industry": row.get("INDUSTRY", ""),
                }
                for row in data["Table"]
            ]
        return []

    async def get_historical_data(self, symbol: str, days: int = 365) -> pd.DataFrame:
        """Get historical data via yfinance BSE fallback."""
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}.BO")
            df = ticker.history(period=f"{days}d")
            if not df.empty:
                df.index = pd.to_datetime(df.index)
                return df[["Open", "High", "Low", "Close", "Volume"]]
        except Exception as e:
            print(f"[BSE] Historical yfinance failed for {symbol}: {e}")
        return pd.DataFrame()

    async def close(self):
        if self._client:
            await self._client.aclose()


_bse_client: Optional[BSEClient] = None


def get_bse_client() -> BSEClient:
    global _bse_client
    if _bse_client is None:
        _bse_client = BSEClient()
    return _bse_client
