"""Webcrawler: fetch clothing products from popular Shopify-backed stores,
extract or infer fiber composition, store in SQLite.

Usage: python crawl.py [--max-pages N]
"""

import asyncio
import json
import sys
import httpx

from db import connect
from fibers import analyze
from sites import SITES, SKIP_TITLE_KEYWORDS

PAGE_LIMIT = 250
REQUEST_DELAY = 1.0  # seconds between requests per site, be polite
MAX_PAGES = 40       # per site cap
CONCURRENT_SITES = 8

HEADERS = {
    "User-Agent": "FiberCrawler/1.0 (clothing fiber composition research; contact: iainwinter1@gmail.com)",
    "Accept": "application/json",
}

db_lock = asyncio.Lock()


def product_rows(site, brand, products):
    rows = []
    for p in products:
        title = p.get("title") or ""
        if any(k in title.lower() for k in SKIP_TITLE_KEYWORDS):
            continue
        handle = p.get("handle")
        if not handle:
            continue
        url = f"https://{site}/products/{handle}"
        images = p.get("images") or []
        image = images[0].get("src") if images else None
        variants = p.get("variants") or []
        price = None
        if variants:
            try:
                price = float(variants[0].get("price") or 0) or None
            except (TypeError, ValueError):
                price = None
        category = p.get("product_type") or ""
        fibers, source, summary = analyze(title, p.get("body_html"), p.get("tags"), category)
        rows.append((site, brand, title, url, image, price, category,
                     json.dumps(fibers), source, summary))
    return rows


async def crawl_site(client, conn, site, brand, max_pages):
    inserted = 0
    for page in range(1, max_pages + 1):
        url = f"https://{site}/products.json?limit={PAGE_LIMIT}&page={page}"
        try:
            resp = await client.get(url)
        except httpx.HTTPError as e:
            print(f"[{brand}] network error page {page}: {e}", flush=True)
            break
        if resp.status_code != 200:
            print(f"[{brand}] HTTP {resp.status_code} page {page}, stopping site", flush=True)
            break
        try:
            products = resp.json().get("products", [])
        except (json.JSONDecodeError, ValueError):
            print(f"[{brand}] non-JSON response page {page}, stopping site", flush=True)
            break
        if not products:
            break

        rows = product_rows(site, brand, products)
        async with db_lock:
            cur = conn.executemany(
                """INSERT OR IGNORE INTO products
                   (site, brand, title, url, image, price, category, fibers, fiber_source, fiber_summary)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                rows,
            )
            conn.commit()
            inserted += cur.rowcount
            total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        print(f"[{brand}] page {page}: +{len(rows)} products (db total: {total})", flush=True)
        await asyncio.sleep(REQUEST_DELAY)
    print(f"[{brand}] done, inserted {inserted}", flush=True)
    return inserted


async def main():
    max_pages = MAX_PAGES
    if "--max-pages" in sys.argv:
        max_pages = int(sys.argv[sys.argv.index("--max-pages") + 1])

    conn = connect()
    sem = asyncio.Semaphore(CONCURRENT_SITES)

    async def bounded(site, brand):
        async with sem:
            try:
                return await crawl_site(client, conn, site, brand, max_pages)
            except Exception as e:
                print(f"[{brand}] failed: {e}", flush=True)
                return 0

    async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
        results = await asyncio.gather(*(bounded(s, b) for s, b in SITES))

    total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    by_source = conn.execute(
        "SELECT fiber_source, COUNT(*) FROM products GROUP BY fiber_source"
    ).fetchall()
    print(f"\nCrawl complete. {sum(results)} new rows this run, {total} total.")
    for source, count in by_source:
        print(f"  {source}: {count}")
    conn.close()


if __name__ == "__main__":
    asyncio.run(main())
