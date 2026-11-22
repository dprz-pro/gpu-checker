from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import Listing

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (id INTEGER PRIMARY KEY, ts TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS observations (
    run_id INTEGER NOT NULL REFERENCES runs(id),
    store TEXT NOT NULL, title TEXT NOT NULL,
    price REAL, in_stock INTEGER NOT NULL, url TEXT NOT NULL
);
"""


def connect(path: str | Path = "data/prices.db") -> sqlite3.Connection:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.executescript(SCHEMA)
    return con


def save_run(con: sqlite3.Connection, listings: list[Listing], ts: datetime | None = None) -> int:
    ts = ts or datetime.now(timezone.utc)
    cur = con.execute("INSERT INTO runs (ts) VALUES (?)", (ts.isoformat(timespec="seconds"),))
    run_id = cur.lastrowid
    con.executemany(
        "INSERT INTO observations VALUES (?,?,?,?,?,?)",
        [(run_id, l.store, l.title, l.price, int(l.in_stock), l.url) for l in listings],
    )
    con.commit()
    return run_id


def load_runs(con: sqlite3.Connection) -> list[tuple[int, str, list[Listing]]]:
    runs = []
    for run_id, ts in con.execute("SELECT id, ts FROM runs ORDER BY id"):
        rows = con.execute(
            "SELECT store, title, price, in_stock, url FROM observations WHERE run_id=?", (run_id,)
        ).fetchall()
        runs.append((run_id, ts, [Listing(s, t, p, bool(i), u) for s, t, p, i, u in rows]))
    return runs
