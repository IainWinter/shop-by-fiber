"""SQLite schema and helpers shared by crawler and web app."""

import os
import sqlite3
import pathlib

# Default to <repo>/data/fiber.db for local dev; override with FIBER_DB in
# containers (compose sets FIBER_DB=/data/fiber.db against a mounted volume).
DB_PATH = pathlib.Path(
    os.environ.get("FIBER_DB", pathlib.Path(__file__).resolve().parent.parent / "data" / "fiber.db")
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    site TEXT NOT NULL,
    brand TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    image TEXT,
    price REAL,
    category TEXT,
    fibers TEXT NOT NULL,          -- JSON: [{"fiber": "cotton", "pct": 95.0, "note": ...}]
    fiber_source TEXT NOT NULL,    -- parsed | inferred | unknown
    fiber_summary TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_products_source ON products(fiber_source);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);

CREATE VIRTUAL TABLE IF NOT EXISTS products_fts USING fts5(
    title, brand, fiber_summary, category,
    content=products, content_rowid=id
);

CREATE TRIGGER IF NOT EXISTS products_ai AFTER INSERT ON products BEGIN
    INSERT INTO products_fts(rowid, title, brand, fiber_summary, category)
    VALUES (new.id, new.title, new.brand, new.fiber_summary, new.category);
END;
CREATE TRIGGER IF NOT EXISTS products_au AFTER UPDATE ON products BEGIN
    INSERT INTO products_fts(products_fts, rowid, title, brand, fiber_summary, category)
    VALUES ('delete', old.id, old.title, old.brand, old.fiber_summary, old.category);
    INSERT INTO products_fts(rowid, title, brand, fiber_summary, category)
    VALUES (new.id, new.title, new.brand, new.fiber_summary, new.category);
END;
CREATE TRIGGER IF NOT EXISTS products_ad AFTER DELETE ON products BEGIN
    INSERT INTO products_fts(products_fts, rowid, title, brand, fiber_summary, category)
    VALUES ('delete', old.id, old.title, old.brand, old.fiber_summary, old.category);
END;
"""


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn
