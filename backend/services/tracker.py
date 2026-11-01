"""
Entry/Exit Tracker — records daily screener snapshots and detects changes.
"""

import json
from datetime import datetime, date
from typing import List, Dict, Optional
from ..database.db import get_db


FILTER_KEY_DEFAULT = "rs80_ema200"


def save_snapshot(symbols: List[str], filter_key: str = FILTER_KEY_DEFAULT):
    """Save today's screener result symbols."""
    conn = get_db()
    today = date.today().isoformat()
    symbols_json = json.dumps(sorted(symbols))
    
    conn.execute(
        """INSERT OR REPLACE INTO screener_snapshots 
           (snapshot_date, filter_key, symbols) VALUES (?, ?, ?)""",
        (today, filter_key, symbols_json)
    )
    conn.commit()
    conn.close()


def get_snapshot(snapshot_date: str, filter_key: str = FILTER_KEY_DEFAULT) -> List[str]:
    """Get symbols from a specific date's snapshot."""
    conn = get_db()
    row = conn.execute(
        "SELECT symbols FROM screener_snapshots WHERE snapshot_date=? AND filter_key=?",
        (snapshot_date, filter_key)
    ).fetchone()
    conn.close()
    if row:
        return json.loads(row["symbols"])
    return []


def detect_changes(filter_key: str = FILTER_KEY_DEFAULT) -> Dict:
    """Compare today's snapshot with yesterday's to find entries and exits."""
    from datetime import timedelta
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    today_syms = set(get_snapshot(today, filter_key))
    yesterday_syms = set(get_snapshot(yesterday, filter_key))
    
    if not yesterday_syms:
        # Try to find the most recent previous snapshot
        conn = get_db()
        rows = conn.execute(
            """SELECT snapshot_date FROM screener_snapshots 
               WHERE filter_key=? AND snapshot_date < ? 
               ORDER BY snapshot_date DESC LIMIT 1""",
            (filter_key, today)
        ).fetchall()
        conn.close()
        if rows:
            yesterday_syms = set(get_snapshot(rows[0]["snapshot_date"], filter_key))

    entering = sorted(today_syms - yesterday_syms)
    exiting = sorted(yesterday_syms - today_syms)
    
    return {
        "date": today,
        "entering": entering,
        "exiting": exiting,
        "entering_count": len(entering),
        "exiting_count": len(exiting),
        "total_today": len(today_syms),
        "total_yesterday": len(yesterday_syms),
    }


def get_symbol_history(symbol: str, filter_key: str = FILTER_KEY_DEFAULT) -> List[Dict]:
    """Get the history of when a symbol entered/exited a screener list."""
    conn = get_db()
    rows = conn.execute(
        """SELECT snapshot_date, symbols FROM screener_snapshots 
           WHERE filter_key=? ORDER BY snapshot_date ASC""",
        (filter_key,)
    ).fetchall()
    conn.close()
    
    history = []
    was_in_list = False
    
    for row in rows:
        symbols = json.loads(row["symbols"])
        is_in_list = symbol in symbols
        
        if is_in_list and not was_in_list:
            history.append({"date": row["snapshot_date"], "event": "entry"})
        elif not is_in_list and was_in_list:
            history.append({"date": row["snapshot_date"], "event": "exit"})
        
        was_in_list = is_in_list
    
    return history


def get_all_snapshots_summary(filter_key: str = FILTER_KEY_DEFAULT) -> List[Dict]:
    """Get summary of all snapshots for tracker timeline view."""
    conn = get_db()
    rows = conn.execute(
        """SELECT snapshot_date, symbols FROM screener_snapshots
           WHERE filter_key=? ORDER BY snapshot_date DESC LIMIT 60""",
        (filter_key,)
    ).fetchall()
    conn.close()
    
    return [
        {
            "date": row["snapshot_date"],
            "count": len(json.loads(row["symbols"])),
        }
        for row in rows
    ]


def get_recent_movers(filter_key: str = FILTER_KEY_DEFAULT, days: int = 7) -> Dict:
    """Get symbols that entered or exited in the last N days."""
    from datetime import timedelta
    conn = get_db()
    
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    rows = conn.execute(
        """SELECT snapshot_date, symbols FROM screener_snapshots
           WHERE filter_key=? AND snapshot_date >= ?
           ORDER BY snapshot_date ASC""",
        (filter_key, cutoff)
    ).fetchall()
    conn.close()
    
    if len(rows) < 2:
        return {"entering": [], "exiting": []}
    
    first_syms = set(json.loads(rows[0]["symbols"]))
    last_syms = set(json.loads(rows[-1]["symbols"]))
    
    return {
        "entering": sorted(last_syms - first_syms),
        "exiting": sorted(first_syms - last_syms),
        "period_days": days,
    }
