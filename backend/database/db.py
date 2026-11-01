import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import pandas as pd

DB_PATH = Path(__file__).parent.parent.parent / "data" / "screener.db"


def get_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Stock universe table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            exchange TEXT,
            sector TEXT,
            industry TEXT,
            sub_industry TEXT,
            isin TEXT,
            updated_at TEXT
        )
    """)

    # Daily OHLCV snapshots
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            market_cap REAL,
            pe REAL,
            UNIQUE(symbol, date)
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_daily_prices_sym_date ON daily_prices(symbol, date)")

    # RS ratings history
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rs_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            date TEXT,
            rs_rating INTEGER,
            rs_3m INTEGER,
            rs_6m INTEGER,
            rs_12m INTEGER,
            UNIQUE(symbol, date)
        )
    """)

    # Screener snapshots for entry/exit tracking
    cur.execute("""
        CREATE TABLE IF NOT EXISTS screener_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_date TEXT,
            filter_key TEXT,
            symbols TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Entry/exit events
    cur.execute("""
        CREATE TABLE IF NOT EXISTS entry_exit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            event_type TEXT,
            filter_key TEXT,
            event_date TEXT,
            close_price REAL,
            rs_rating INTEGER,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Pre-calculated stock screener metrics (persisted for instant serving)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS screener_metrics (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            exchange TEXT,
            sector TEXT,
            industry TEXT,
            sub_industry TEXT,
            close REAL,
            prev_close REAL,
            market_cap REAL,
            pe REAL,
            rs_rating INTEGER,
            rs_3m INTEGER,
            rs_6m INTEGER,
            rs_12m INTEGER,
            rs_score_raw REAL,
            from_52w_high REAL,
            above_ema50 INTEGER,
            above_ema200 INTEGER,
            avg_turnover_cr REAL,
            volume_surge INTEGER,
            return_1d REAL,
            return_1w REAL,
            return_1m REAL,
            return_3m REAL,
            return_6m REAL,
            return_1y REAL,
            updated_at TEXT
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_metrics_rs ON screener_metrics(rs_rating DESC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_metrics_sector ON screener_metrics(sector)")

    # System sync status tracking
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sync_status (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            status TEXT,
            progress TEXT,
            total INTEGER,
            current INTEGER,
            message TEXT,
            last_synced TEXT
        )
    """)

    # Company quarterly financial results cache
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_financials (
            symbol TEXT PRIMARY KEY,
            quarters_json TEXT,
            rows_json TEXT,
            source TEXT,
            updated_at TEXT
        )
    """)

    # Company shareholding patterns cache
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_shareholding (
            symbol TEXT PRIMARY KEY,
            quarters_json TEXT,
            rows_json TEXT,
            latest_json TEXT,
            source TEXT,
            updated_at TEXT
        )
    """)

    # Company key ratios (Market Cap, PE, 52W High/Low, Book Value, etc.) cache
    cur.execute("""
        CREATE TABLE IF NOT EXISTS company_ratios (
            symbol TEXT PRIMARY KEY,
            ratios_json TEXT,
            updated_at TEXT
        )
    """)

    # Initialize sync status row if missing
    cur.execute("""
        INSERT OR IGNORE INTO sync_status (id, status, progress, total, current, message, last_synced)
        VALUES (1, 'idle', '0%', 0, 0, 'Not started', NULL)
    """)

    conn.commit()
    conn.close()
    print(f"[DB] Initialized at {DB_PATH}")


def save_screener_metrics(metrics: List[Dict]):
    """Upsert pre-calculated screener metrics."""
    if not metrics:
        return
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.now().isoformat()

    cur.executemany("""
        INSERT OR REPLACE INTO screener_metrics (
            symbol, name, exchange, sector, industry, sub_industry,
            close, prev_close, market_cap, pe,
            rs_rating, rs_3m, rs_6m, rs_12m, rs_score_raw,
            from_52w_high, above_ema50, above_ema200,
            avg_turnover_cr, volume_surge,
            return_1d, return_1w, return_1m, return_3m, return_6m, return_1y,
            updated_at
        ) VALUES (
            :symbol, :name, :exchange, :sector, :industry, :sub_industry,
            :close, :prev_close, :market_cap, :pe,
            :rs_rating, :rs_3m, :rs_6m, :rs_12m, :rs_score_raw,
            :from_52w_high, :above_ema50, :above_ema200,
            :avg_turnover_cr, :volume_surge,
            :return_1d, :return_1w, :return_1m, :return_3m, :return_6m, :return_1y,
            :updated_at
        )
    """, [{**m, "updated_at": now_str} for m in metrics])

    conn.commit()
    conn.close()


def load_all_screener_metrics(exchange: str = "NSE") -> List[Dict]:
    """Load pre-calculated screener metrics from DB, sorted by RS rating descending."""
    conn = get_db()
    cur = conn.cursor()
    if exchange == "BOTH":
        cur.execute("SELECT * FROM screener_metrics ORDER BY rs_rating DESC")
    else:
        cur.execute("""
            SELECT * FROM screener_metrics 
            WHERE exchange = ? OR exchange = 'BOTH'
            ORDER BY rs_rating DESC
        """, (exchange,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_daily_prices(price_map: Dict[str, pd.DataFrame]):
    """Store daily price rows in SQLite for chart rendering and offline metrics."""
    if not price_map:
        return
    conn = get_db()
    cur = conn.cursor()

    rows = []
    for sym, df in price_map.items():
        if df.empty:
            continue
        for ts, row in df.iterrows():
            d_str = ts.strftime("%Y-%m-%d") if hasattr(ts, 'strftime') else str(ts)[:10]
            rows.append((
                sym,
                d_str,
                float(row.get("Open", row.get("Close", 0))),
                float(row.get("High", row.get("Close", 0))),
                float(row.get("Low", row.get("Close", 0))),
                float(row.get("Close", 0)),
                float(row.get("Volume", 0) or 0),
            ))

    cur.executemany("""
        INSERT OR REPLACE INTO daily_prices (symbol, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()


def get_daily_candles(symbol: str, days: int = 365) -> List[Dict]:
    """Retrieve daily candles for chart."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, open, high, low, close, volume
        FROM daily_prices
        WHERE symbol = ?
        ORDER BY date ASC
    """, (symbol.upper(),))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return []

    candles = []
    for r in rows[-days:]:
        try:
            dt = datetime.strptime(r["date"], "%Y-%m-%d")
            candles.append({
                "time": int(dt.timestamp()),
                "open": round(r["open"], 2),
                "high": round(r["high"], 2),
                "low": round(r["low"], 2),
                "close": round(r["close"], 2),
                "volume": int(r["volume"] or 0),
            })
        except Exception:
            continue
    return candles


def set_sync_status(status: str, progress: str = "0%", total: int = 0, current: int = 0, message: str = ""):
    """Update background sync status."""
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        UPDATE sync_status
        SET status = ?, progress = ?, total = ?, current = ?, message = ?, last_synced = CASE WHEN ? = 'completed' THEN ? ELSE last_synced END
        WHERE id = 1
    """, (status, progress, total, current, message, status, now_str))
    conn.commit()
    conn.close()


def get_sync_status() -> Dict:
    """Get current sync status."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT status, progress, total, current, message, last_synced FROM sync_status WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"status": "idle", "progress": "0%", "total": 0, "current": 0, "message": "Unknown", "last_synced": None}


def get_cached_company_financials(symbol: str) -> Optional[Dict]:
    """Retrieve cached quarterly financial results from SQLite."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT quarters_json, rows_json, source, updated_at
        FROM company_financials
        WHERE symbol = ?
    """, (symbol.upper(),))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    try:
        return {
            "symbol": symbol.upper(),
            "quarters": json.loads(row["quarters_json"]),
            "rows": json.loads(row["rows_json"]),
            "source": row["source"],
            "updated_at": row["updated_at"],
        }
    except Exception:
        return None


def save_cached_company_financials(symbol: str, quarters: List[str], rows: List[Dict], source: str = "screener"):
    """Store quarterly financial results in SQLite."""
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.now().isoformat()
    cur.execute("""
        INSERT OR REPLACE INTO company_financials (symbol, quarters_json, rows_json, source, updated_at)
        VALUES (?, ?, ?, ?, ?)
    """, (symbol.upper(), json.dumps(quarters), json.dumps(rows), source, now_str))
    conn.commit()
    conn.close()


def get_cached_company_shareholding(symbol: str) -> Optional[Dict]:
    """Retrieve cached shareholding patterns from SQLite."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT quarters_json, rows_json, latest_json, source, updated_at
        FROM company_shareholding
        WHERE symbol = ?
    """, (symbol.upper(),))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    try:
        return {
            "symbol": symbol.upper(),
            "quarters": json.loads(row["quarters_json"]),
            "rows": json.loads(row["rows_json"]),
            "latest": json.loads(row["latest_json"]) if row["latest_json"] else {},
            "source": row["source"],
            "updated_at": row["updated_at"],
        }
    except Exception:
        return None


def save_cached_company_shareholding(symbol: str, quarters: List[str], rows: List[Dict], latest: Dict, source: str = "screener"):
    """Store shareholding patterns in SQLite."""
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.now().isoformat()
    cur.execute("""
        INSERT OR REPLACE INTO company_shareholding (symbol, quarters_json, rows_json, latest_json, source, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (symbol.upper(), json.dumps(quarters), json.dumps(rows), json.dumps(latest), source, now_str))
    conn.commit()
    conn.close()


def get_cached_company_ratios(symbol: str) -> Optional[Dict]:
    """Retrieve cached key ratios from SQLite."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT ratios_json FROM company_ratios WHERE symbol = ?", (symbol.upper(),))
    row = cur.fetchone()
    conn.close()
    if row and row["ratios_json"]:
        try:
            return json.loads(row["ratios_json"])
        except Exception:
            return None
    return None


def save_cached_company_ratios(symbol: str, ratios: Dict):
    """Store key ratios in SQLite."""
    conn = get_db()
    cur = conn.cursor()
    now_str = datetime.now().isoformat()
    cur.execute("""
        INSERT OR REPLACE INTO company_ratios (symbol, ratios_json, updated_at)
        VALUES (?, ?, ?)
    """, (symbol.upper(), json.dumps(ratios), now_str))
    conn.commit()
    conn.close()
