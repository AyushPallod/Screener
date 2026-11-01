"""
NSE Data Client — fetches data from NSE India with fallbacks.
Priority: nsepython → NSE official JSON APIs → yfinance
"""

import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import asyncio
import json

NSE_BASE = "https://www.nseindia.com/api"
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.nseindia.com/market-data/live-equity-market",
    "Connection": "keep-alive",
}


class NSEClient:
    def __init__(self):
        self._session_cookies: dict = {}
        self._client: Optional[httpx.AsyncClient] = None
        self._last_cookie_refresh = datetime.min

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=NSE_HEADERS,
                timeout=30,
                follow_redirects=True,
            )
        # Refresh cookies every 30 minutes
        if (datetime.now() - self._last_cookie_refresh).seconds > 1800:
            await self._refresh_cookies()
        return self._client

    async def _refresh_cookies(self):
        try:
            client = self._client or httpx.AsyncClient(headers=NSE_HEADERS, timeout=15)
            resp = await client.get("https://www.nseindia.com")
            self._session_cookies = dict(resp.cookies)
            self._last_cookie_refresh = datetime.now()
        except Exception as e:
            print(f"[NSE] Cookie refresh failed: {e}")

    async def _get(self, url: str) -> Optional[dict]:
        try:
            client = await self._get_client()
            resp = await client.get(url, cookies=self._session_cookies)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[NSE] GET {url} failed: {e}")
        return None

    async def get_equity_market_data(self, index: str = "NIFTY 500") -> List[Dict]:
        """Get live market data for all stocks in an index."""
        url = f"{NSE_BASE}/live-analysis-variations?index={index.replace(' ', '%20')}"
        data = await self._get(url)
        if data and "data" in data:
            return data["data"]
        return []

    async def get_all_nse_symbols(self) -> List[Dict]:
        """Get full NSE equity list with sector/industry info."""
        url = f"{NSE_BASE}/equity-master"
        data = await self._get(url)
        if data:
            stocks = []
            for sector, companies in data.items():
                for sym, name in companies.items():
                    stocks.append({
                        "symbol": sym,
                        "name": name,
                        "exchange": "NSE",
                        "sector": sector,
                    })
            return stocks
        return []

    async def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get detailed quote for a single NSE stock."""
        url = f"{NSE_BASE}/quote-equity?symbol={symbol}"
        data = await self._get(url)
        if data and "priceInfo" in data:
            pi = data["priceInfo"]
            metadata = data.get("metadata", {})
            return {
                "symbol": symbol,
                "name": metadata.get("companyName", symbol),
                "close": pi.get("lastPrice", 0),
                "open": pi.get("open", 0),
                "high": pi.get("intraDayHighLow", {}).get("max", 0),
                "low": pi.get("intraDayHighLow", {}).get("min", 0),
                "prev_close": pi.get("previousClose", 0),
                "change_pct": pi.get("pChange", 0),
                "market_cap": metadata.get("pdMarketCap", 0),
                "pe": metadata.get("pdPe", None),
                "52w_high": pi.get("weekHighLow", {}).get("max", 0),
                "52w_low": pi.get("weekHighLow", {}).get("min", 0),
                "volume": data.get("securityWiseDP", {}).get("quantityTraded", 0),
            }
        return None

    async def get_historical_data(self, symbol: str, days: int = 365) -> pd.DataFrame:
        """Get historical OHLCV data for RS calculation."""
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}.NS")
            df = ticker.history(period=f"{days}d")
            if not df.empty:
                df.index = pd.to_datetime(df.index)
                return df[["Open", "High", "Low", "Close", "Volume"]]
        except Exception as e:
            print(f"[NSE] Historical fallback (yfinance) failed for {symbol}: {e}")
        return pd.DataFrame()

    async def get_nse_indices(self) -> List[Dict]:
        """Get list of NSE indices."""
        url = f"{NSE_BASE}/allIndices"
        data = await self._get(url)
        if data and "data" in data:
            return data["data"]
        return []

    async def get_nifty500_stocks(self) -> List[Dict]:
        """Get Nifty 500 component stocks with sector."""
        url = f"{NSE_BASE}/equity-stockIndices?index=NIFTY%20500"
        data = await self._get(url)
        if data and "data" in data:
            return data["data"]
        return []

    async def close(self):
        if self._client:
            await self._client.aclose()


# Singleton
_nse_client: Optional[NSEClient] = None


def get_nse_client() -> NSEClient:
    global _nse_client
    if _nse_client is None:
        _nse_client = NSEClient()
    return _nse_client
