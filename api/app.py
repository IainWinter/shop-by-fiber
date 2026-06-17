"""Fiber search API: query the crawled clothing DB by text and fiber.

The frontend is a separate Astro static site (deployed to GitHub Pages at
shopbyfiber.com); this service is API-only.

Usage: python -m uvicorn app:app --port 8000  (from api/ directory)
"""

import json
import sqlite3

from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from db import DB_PATH
from affiliates import affiliate_url

app = FastAPI(title="ShopByFiber API — search clothes by material")

# Allow the GitHub Pages frontend (served from the apex + www) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://shopbyfiber.com", "https://www.shopbyfiber.com"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

FIBERS = [
    "cotton", "polyester", "nylon", "spandex", "merino wool", "wool", "cashmere",
    "silk", "linen", "hemp", "viscose", "modal", "lyocell", "acrylic", "down",
    "alpaca", "leather",
]


def query_db(sql, params=()):
    # immutable=1: serve a static, read-only DB without needing to create the
    # WAL/-shm sidecars — required when the DB is on a read-only mount.
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro&immutable=1", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


@app.get("/")
def index():
    # No static site here — send humans to the frontend.
    return RedirectResponse("https://shopbyfiber.com")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/fibers")
def fibers():
    return FIBERS


@app.get("/api/stats")
def stats():
    rows = query_db("SELECT fiber_source, COUNT(*) AS n FROM products GROUP BY fiber_source")
    total = sum(r["n"] for r in rows)
    return {"total": total, "by_source": {r["fiber_source"]: r["n"] for r in rows}}


@app.get("/api/search")
def search(
    q: str = Query("", max_length=200),
    fiber: str = Query("", max_length=50),
    source: str = Query("", pattern="^(parsed|inferred|unknown)?$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(24, ge=1, le=100),
):
    where, params = [], []

    if q.strip():
        # FTS5 prefix match on each term; quote terms to neutralize FTS syntax
        terms = [t.replace('"', "") for t in q.split() if t.strip('"')]
        match = " ".join(f'"{t}"*' for t in terms)
        where.append("p.id IN (SELECT rowid FROM products_fts WHERE products_fts MATCH ?)")
        params.append(match)

    if fiber.strip():
        where.append("EXISTS (SELECT 1 FROM json_each(p.fibers) je WHERE json_extract(je.value, '$.fiber') = ?)")
        params.append(fiber.strip().lower())

    if source:
        where.append("p.fiber_source = ?")
        params.append(source)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    count = query_db(f"SELECT COUNT(*) AS n FROM products p {where_sql}", params)[0]["n"]
    rows = query_db(
        f"""SELECT p.id, p.site, p.brand, p.title, p.url, p.image, p.price,
                   p.category, p.fibers, p.fiber_source, p.fiber_summary
            FROM products p {where_sql}
            ORDER BY p.fiber_source = 'parsed' DESC, p.id
            LIMIT ? OFFSET ?""",
        params + [per_page, (page - 1) * per_page],
    )
    for r in rows:
        r["fibers"] = json.loads(r["fibers"])
        r["url"] = affiliate_url(r["url"])
    return {"total": count, "page": page, "per_page": per_page, "results": rows}
