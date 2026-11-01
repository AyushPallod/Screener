import re
import json
import logging
from datetime import datetime
import requests
from typing import Dict, List, Optional, Tuple, Any
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf

from ..database.db import (
    get_cached_company_financials,
    save_cached_company_financials,
    get_cached_company_shareholding,
    save_cached_company_shareholding,
    get_cached_company_ratios,
    save_cached_company_ratios,
    get_daily_candles,
)
from ..data.stock_universe import get_meta, ALIASES

TICKER_RENAMES = ALIASES

logger = logging.getLogger("financial_service")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}


def _resolve_symbol(symbol: str) -> str:
    """Resolve symbol using aliases and ticker renames."""
    sym = symbol.upper()
    return TICKER_RENAMES.get(sym, sym)


def _resolve_yf_symbol(symbol: str) -> str:
    """Resolve Yahoo Finance ticker for symbol including SME and BSE formats."""
    sym = _resolve_symbol(symbol)
    meta = get_meta(sym)
    if meta.get("yf_symbol"):
        return meta["yf_symbol"]
    if sym.isdigit():
        return f"{sym}.BO"
    return f"{sym}.NS"


def _parse_quarter_date(q_str: str) -> Tuple[int, int]:
    """Parse 'Sep 2026' or '2026-09' into (year, month). Returns (0, 0) if unparseable."""
    if not q_str:
        return (0, 0)
    month_map = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    parts = q_str.strip().split()
    if len(parts) >= 2:
        m_str = parts[0][:3].lower()
        y_str = parts[1]
        m = month_map.get(m_str, 0)
        try:
            y = int(re.sub(r"\D", "", y_str))
            return (y, m)
        except Exception:
            return (0, 0)
    return (0, 0)


def _get_latest_quarter_from_soup(soup: BeautifulSoup) -> Tuple[int, int]:
    """Inspect quarters table in Screener page and return (year, month) of latest column."""
    try:
        q_sec = soup.find("section", {"id": "quarters"})
        if q_sec and q_sec.find("table"):
            table = q_sec.find("table")
            thead = table.find("thead")
            if thead:
                ths = [th.get_text(strip=True) for th in thead.find_all("th") if th.get_text(strip=True)]
                if ths:
                    return _parse_quarter_date(ths[-1])
    except Exception:
        pass
    return (0, 0)


def _fetch_screener_soup(symbol: str) -> Optional[BeautifulSoup]:
    """
    Fetch Screener.in page HTML.
    Fetches both consolidated and standalone versions and picks the one with the
    most recent quarterly results (crucial when standalone reports e.g. Sep 2026
    before consolidated is finalized, or for SME stocks).
    """
    sym = _resolve_symbol(symbol)
    con_soup = None
    sta_soup = None

    try:
        r_con = requests.get(f"https://www.screener.in/company/{sym}/consolidated/", headers=HEADERS, timeout=4)
        if r_con.status_code == 200 and "screener" in r_con.text.lower():
            con_soup = BeautifulSoup(r_con.text, "html.parser")
    except Exception:
        pass

    try:
        r_sta = requests.get(f"https://www.screener.in/company/{sym}/", headers=HEADERS, timeout=4)
        if r_sta.status_code == 200 and "screener" in r_sta.text.lower():
            sta_soup = BeautifulSoup(r_sta.text, "html.parser")
    except Exception:
        pass

    if con_soup and sta_soup:
        q_con = _get_latest_quarter_from_soup(con_soup)
        q_sta = _get_latest_quarter_from_soup(sta_soup)
        # Standalone takes precedence if it has a strictly newer reported quarter
        if q_sta > q_con:
            return sta_soup
        return con_soup

    if con_soup:
        return con_soup
    if sta_soup:
        return sta_soup

    # Fallback to search query
    try:
        search_url = f"https://www.screener.in/api/company/search/?q={sym}"
        r = requests.get(search_url, headers=HEADERS, timeout=3)
        if r.status_code == 200:
            results = r.json()
            if results and isinstance(results, list):
                target_url = results[0].get("url")
                if target_url:
                    full_url = f"https://www.screener.in{target_url}"
                    r_target = requests.get(full_url, headers=HEADERS, timeout=4)
                    if r_target.status_code == 200:
                        return BeautifulSoup(r_target.text, "html.parser")
    except Exception as e:
        logger.warning(f"[FinancialService] Screener search failed for {sym}: {e}")

    return None


def fetch_financials_from_yfinance(symbol: str) -> Dict[str, Any]:
    """Fallback: retrieve quarterly financials from yfinance."""
    sym = _resolve_symbol(symbol)
    yf_sym = _resolve_yf_symbol(sym)
    ticker = yf.Ticker(yf_sym)
    quarters: List[str] = []
    rows: List[Dict[str, Any]] = []

    try:
        stmt = ticker.quarterly_income_stmt
        if stmt is not None and not stmt.empty:
            cols = [
                col.strftime("%b %Y") if hasattr(col, "strftime") else str(col)[:7]
                for col in stmt.columns
            ]
            # Order chronologically and keep up to last 8 quarters
            cols = cols[::-1][-8:]
            quarters = cols

            metric_map = [
                ("Sales / Revenue", "Total Revenue", 1e7, "Cr"),
                ("Operating Profit", "Operating Income", 1e7, "Cr"),
                ("EBITDA", "EBITDA", 1e7, "Cr"),
                ("Depreciation", "Reconciled Depreciation", 1e7, "Cr"),
                ("Interest Expense", "Interest Expense", 1e7, "Cr"),
                ("Profit before tax", "Pretax Income", 1e7, "Cr"),
                ("Tax Provision", "Tax Provision", 1e7, "Cr"),
                ("Net Profit", "Net Income", 1e7, "Cr"),
                ("EPS in Rs", "Diluted EPS", 1.0, ""),
            ]

            for display_name, yf_name, div, unit in metric_map:
                if yf_name in stmt.index:
                    vals = []
                    for col in stmt.columns[::-1][-8:]:
                        v = stmt.loc[yf_name, col]
                        if pd.notna(v):
                            num = round(float(v) / div, 1) if div != 1.0 else round(float(v), 2)
                            vals.append(f"{num:,.2f}" if div == 1.0 else f"{num:,.1f}")
                        else:
                            vals.append("—")
                    rows.append({"name": display_name, "values": vals, "unit": unit})

            # Calculate OPM % if Sales and Operating Profit exist
            sales_row = next((r for r in rows if r["name"] == "Sales / Revenue"), None)
            op_row = next((r for r in rows if r["name"] == "Operating Profit"), None)
            if sales_row and op_row:
                opm_vals = []
                for s_val, op_val in zip(sales_row["values"], op_row["values"]):
                    try:
                        s_clean = float(s_val.replace(",", ""))
                        op_clean = float(op_val.replace(",", ""))
                        if s_clean > 0:
                            opm_vals.append(f"{round((op_clean / s_clean) * 100, 1)}%")
                        else:
                            opm_vals.append("—")
                    except Exception:
                        opm_vals.append("—")
                rows.insert(2, {"name": "OPM %", "values": opm_vals, "unit": "%"})

    except Exception as e:
        logger.warning(f"[FinancialService] yfinance quarterly_income_stmt failed for {sym}: {e}")

    return {
        "symbol": sym,
        "quarters": quarters,
        "rows": rows,
        "source": "yfinance",
    }


def fetch_shareholding_from_yfinance(symbol: str) -> Dict[str, Any]:
    """Fallback: retrieve shareholding pattern from yfinance major_holders / info."""
    sym = _resolve_symbol(symbol)
    yf_sym = _resolve_yf_symbol(sym)
    ticker = yf.Ticker(yf_sym)
    quarters = ["Latest"]
    rows: List[Dict[str, Any]] = []
    latest: Dict[str, Any] = {}

    try:
        info = ticker.info or {}
        p_insiders = float(info.get("heldPercentInsiders") or 0.0)
        p_institutions = float(info.get("heldPercentInstitutions") or 0.0)

        promoters = round(p_insiders * 100, 2)
        inst_total = round(p_institutions * 100, 2)
        public = max(0.0, round(100.0 - promoters - inst_total, 2))

        # Standard Indian institutional split estimate
        fiis = round(inst_total * 0.55, 2)
        diis = round(inst_total - fiis, 2)

        latest = {
            "quarter": "Latest",
            "promoters": promoters,
            "fiis": fiis,
            "diis": diis,
            "government": 0.0,
            "public": public,
        }

        rows = [
            {"name": "Promoters", "values": [f"{promoters}%"]},
            {"name": "FIIs", "values": [f"{fiis}%"]},
            {"name": "DIIs", "values": [f"{diis}%"]},
            {"name": "Public", "values": [f"{public}%"]},
        ]
    except Exception as e:
        logger.warning(f"[FinancialService] yfinance shareholding failed for {sym}: {e}")

    return {
        "symbol": sym,
        "quarters": quarters,
        "rows": rows,
        "latest": latest,
        "source": "yfinance",
    }


def get_company_financials(symbol: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Get quarterly financial results, checking SQLite cache first."""
    sym = _resolve_symbol(symbol)

    if not force_refresh:
        cached = get_cached_company_financials(sym)
        if cached and cached.get("quarters") and cached.get("rows"):
            # Check if cache is older than 24 hours
            updated_at = cached.get("updated_at")
            is_stale = False
            if updated_at:
                try:
                    dt = datetime.fromisoformat(updated_at)
                    if (datetime.now() - dt).total_seconds() > 86400:
                        is_stale = True
                except Exception:
                    pass
            if not is_stale:
                return cached

    # Attempt Screener.in extraction
    soup = _fetch_screener_soup(sym)
    if soup:
        try:
            q_sec = soup.find("section", {"id": "quarters"})
            if q_sec and q_sec.find("table"):
                table = q_sec.find("table")
                thead = table.find("thead")
                raw_headers = [th.get_text(strip=True) for th in thead.find_all("th")] if thead else []
                all_q = [h for h in raw_headers if h]
                quarters = all_q[-12:] if len(all_q) > 12 else all_q  # Keep up to last 12 quarters
                num_q = len(quarters)

                rows = []
                tbody = table.find("tbody")
                if tbody:
                    for tr in tbody.find_all("tr"):
                        cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
                        if cells:
                            row_name = cells[0].rstrip("+").strip()
                            if row_name.lower() in ["raw pdf", ""]:
                                continue
                            vals = cells[1:][-num_q:]
                            # Determine unit
                            unit = "%" if "%" in row_name else ("₹" if "eps" in row_name.lower() else "₹ Cr")
                            rows.append({
                                "name": row_name,
                                "values": vals,
                                "unit": unit,
                            })

                if quarters and rows:
                    save_cached_company_financials(sym, quarters, rows, "screener")
                    return {
                        "symbol": sym,
                        "quarters": quarters,
                        "rows": rows,
                        "source": "screener",
                    }
        except Exception as e:
            logger.warning(f"[FinancialService] Screener quarterly parse error for {sym}: {e}")

    # Fallback to yfinance
    yf_data = fetch_financials_from_yfinance(sym)
    if yf_data.get("quarters") and yf_data.get("rows"):
        save_cached_company_financials(sym, yf_data["quarters"], yf_data["rows"], "yfinance")
        return yf_data

    return {
        "symbol": sym,
        "quarters": [],
        "rows": [],
        "source": "none",
        "error": "No financial results data available",
    }


def get_company_shareholding(symbol: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Get shareholding pattern (Promoter, FII, DII, Public), checking SQLite cache first."""
    sym = _resolve_symbol(symbol)

    if not force_refresh:
        cached = get_cached_company_shareholding(sym)
        if cached and cached.get("quarters") and cached.get("rows"):
            # Check if cache is older than 24 hours
            updated_at = cached.get("updated_at")
            is_stale = False
            if updated_at:
                try:
                    dt = datetime.fromisoformat(updated_at)
                    if (datetime.now() - dt).total_seconds() > 86400:
                        is_stale = True
                except Exception:
                    pass
            if not is_stale:
                return cached

    # Attempt Screener.in extraction
    soup = _fetch_screener_soup(sym)
    if soup:
        try:
            sh_sec = soup.find("section", {"id": "shareholding"})
            if sh_sec and sh_sec.find("table"):
                table = sh_sec.find("table")
                thead = table.find("thead")
                raw_headers = [th.get_text(strip=True) for th in thead.find_all("th")] if thead else []
                all_sh_q = [h for h in raw_headers if h]
                quarters = all_sh_q[-12:] if len(all_sh_q) > 12 else all_sh_q
                num_q = len(quarters)

                rows = []
                tbody = table.find("tbody")
                latest_dict: Dict[str, Any] = {}

                if tbody:
                    for tr in tbody.find_all("tr"):
                        cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
                        if cells:
                            row_name = cells[0].rstrip("+").strip()
                            vals = cells[1:][-num_q:]
                            rows.append({
                                "name": row_name,
                                "values": vals,
                            })

                    # Parse latest percentages
                    latest_q = quarters[-1] if quarters else "Latest"
                    latest_dict["quarter"] = latest_q

                    for r in rows:
                        name_lower = r["name"].lower()
                        last_val_str = r["values"][-1] if r["values"] else "0"
                        clean_num = 0.0
                        try:
                            clean_num = float(re.sub(r"[^\d.]", "", last_val_str))
                        except Exception:
                            clean_num = 0.0

                        if "promoter" in name_lower:
                            latest_dict["promoters"] = clean_num
                        elif "fii" in name_lower:
                            latest_dict["fiis"] = clean_num
                        elif "dii" in name_lower:
                            latest_dict["diis"] = clean_num
                        elif "government" in name_lower:
                            latest_dict["government"] = clean_num
                        elif "public" in name_lower:
                            latest_dict["public"] = clean_num
                        elif "shareholder" in name_lower:
                            latest_dict["shareholders_count"] = last_val_str

                    # Ensure standard keys exist
                    for k in ["promoters", "fiis", "diis", "government", "public"]:
                        if k not in latest_dict:
                            latest_dict[k] = 0.0

                if quarters and rows:
                    save_cached_company_shareholding(sym, quarters, rows, latest_dict, "screener")
                    return {
                        "symbol": sym,
                        "quarters": quarters,
                        "rows": rows,
                        "latest": latest_dict,
                        "source": "screener",
                    }
        except Exception as e:
            logger.warning(f"[FinancialService] Screener shareholding parse error for {sym}: {e}")

    # Fallback to yfinance
    yf_data = fetch_shareholding_from_yfinance(sym)
    if yf_data.get("quarters") and yf_data.get("rows"):
        save_cached_company_shareholding(sym, yf_data["quarters"], yf_data["rows"], yf_data.get("latest", {}), "yfinance")
        return yf_data

    return {
        "symbol": sym,
        "quarters": [],
        "rows": [],
        "latest": {},
        "source": "none",
        "error": "No shareholding data available",
    }


def get_company_ratios(symbol: str, force_refresh: bool = False) -> Dict[str, Any]:
    """Retrieve key metrics (Market Cap, PE Ratio, 52W High/Low, Book Value, etc.)."""
    sym = _resolve_symbol(symbol)

    if not force_refresh:
        cached = get_cached_company_ratios(sym)
        if cached and cached.get("market_cap") and cached.get("pe") is not None:
            return cached

    ratios = {
        "market_cap": 0.0,
        "pe": None,
        "52w_high": None,
        "52w_low": None,
        "book_value": None,
        "dividend_yield": None,
        "roce": None,
        "roe": None,
    }

    # 1. Try Screener.in top-ratios
    soup = _fetch_screener_soup(sym)
    if soup:
        ul = soup.find("ul", {"id": "top-ratios"})
        if ul:
            for li in ul.find_all("li"):
                name_el = li.find("span", {"class": "name"})
                if not name_el:
                    continue
                name = name_el.get_text(strip=True).lower()

                if "high" in name and "low" in name:
                    numbers = li.find_all("span", {"class": "number"})
                    if len(numbers) >= 2:
                        try:
                            ratios["52w_high"] = float(numbers[0].get_text(strip=True).replace(",", ""))
                            ratios["52w_low"] = float(numbers[1].get_text(strip=True).replace(",", ""))
                        except Exception:
                            pass
                    continue

                num_el = li.find("span", {"class": "number"})
                if not num_el:
                    continue
                num_text = num_el.get_text(strip=True).replace(",", "")
                try:
                    val = float(num_text)
                    if "market cap" in name:
                        ratios["market_cap"] = val
                    elif "stock p/e" in name or "p/e" in name:
                        ratios["pe"] = val
                    elif "book value" in name:
                        ratios["book_value"] = val
                    elif "dividend yield" in name:
                        ratios["dividend_yield"] = val
                    elif "roce" in name:
                        ratios["roce"] = val
                    elif "roe" in name:
                        ratios["roe"] = val
                except Exception:
                    pass

    # 2. Fallback to yfinance if still missing
    if not ratios["market_cap"] or ratios["pe"] is None:
        try:
            yf_sym = _resolve_yf_symbol(sym)
            t = yf.Ticker(yf_sym)
            info = t.info or {}
            if not ratios["market_cap"] and info.get("marketCap"):
                ratios["market_cap"] = round(info["marketCap"] / 1e7, 1)
            if ratios["pe"] is None and (info.get("trailingPE") or info.get("forwardPE")):
                ratios["pe"] = round(float(info.get("trailingPE") or info.get("forwardPE")), 1)
            if ratios["52w_high"] is None and info.get("fiftyTwoWeekHigh"):
                ratios["52w_high"] = float(info["fiftyTwoWeekHigh"])
            if ratios["52w_low"] is None and info.get("fiftyTwoWeekLow"):
                ratios["52w_low"] = float(info["fiftyTwoWeekLow"])
            if ratios["book_value"] is None and info.get("bookValue"):
                ratios["book_value"] = float(info["bookValue"])
            if ratios["dividend_yield"] is None and info.get("dividendYield"):
                ratios["dividend_yield"] = round(float(info["dividendYield"]) * 100, 2)
        except Exception as e:
            logger.warning(f"[FinancialService] yfinance ratios failed for {sym}: {e}")

    # 3. 52W High and Low calculation from daily candles fallback
    if ratios["52w_high"] is None or ratios["52w_low"] is None:
        candles = get_daily_candles(sym, 365)
        if candles:
            if ratios["52w_high"] is None:
                ratios["52w_high"] = round(max(c["high"] for c in candles), 2)
            if ratios["52w_low"] is None:
                ratios["52w_low"] = round(min(c["low"] for c in candles), 2)

    save_cached_company_ratios(sym, ratios)
    return ratios
