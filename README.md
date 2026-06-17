# ShopByFiber

Search for clothes by material. Live at [shopbyfiber.com](https://shopbyfiber.com).

## Layout

- `api/` — FastAPI service + crawler (the deployable backend).
  - `crawl.py` crawls public Shopify `/products.json` endpoints, extracts fiber
    composition from product descriptions, and infers fibers from domain
    knowledge when not stated. Writes to `data/fiber.db` (SQLite + FTS5).
  - `app.py` serves the search API. `affiliates.py` wraps product URLs with
    affiliate tracking (see `AFFILIATE_SIGNUP.md`).
- `web/` — Astro static site (the frontend), deployed to GitHub Pages.
- `data/` — the SQLite DB (not committed; built by the crawler).

The frontend (shopbyfiber.com) is static on GitHub Pages and calls the
self-hosted API at `api.shopbyfiber.com`.

## Develop

API:

```sh
pip install -r api/requirements.txt
cd api && python crawl.py          # build/refresh data/fiber.db (resumable, deduped)
python -m uvicorn app:app --port 8000
```

Frontend:

```sh
cd web
npm install
npm run dev                        # http://localhost:4321 (calls localhost API)
```

## Deploy

Frontend: push to `main` — GitHub Actions builds `web/` and publishes to Pages.

API (self-hosted behind nginx):

```sh
# copy data/fiber.db onto the server first
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
cp nginx/api.shopbyfiber.com.conf /etc/nginx/conf.d/
certbot --nginx -d api.shopbyfiber.com
nginx -t && systemctl reload nginx
```
