# Module : b_import_missing_products.py
# Purpose : importing products functions

from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs
from fastapi import APIRouter, Depends
import requests

from app.core.utils.auth_guard import require_login

router = APIRouter(
    dependencies=[Depends(require_login)]
)

SHOPIFY_API_VERSION = "2026-01"
SHOPIFY_PRODUCTS_LIMIT = 250

def _get_next_page_info(link_header: Optional[str]) -> Optional[Dict[str,str]]:
    if not link_header:
        return None

    parts = [p.strip() for p in link_header.split(",")]
    for part in parts:
        if 'rel="next"' in part:
            start = part.find("<") + 1
            end = part.find(">")
            if start <= 0 or end <= 0:
                return None
            next_url = part[start:end]

            qs = parse_qs(urlparse(next_url).query)
            page_info = qs.get("page_info", [None])[0]
            limit = qs.get("limit", [None])[0]

            if page_info:
                out = {"page_info:": page_info}
                if limit:
                    out["limit"] = limit
                return out
    return None

def fetch_active_products_from_shopify(shop_domain: str, access_token: str) -> List[dict]:
    headers = {"X-Shopify-Access-Token": access_token}

    # First page
    url = f"https://{shop_domain}/admin/api/{SHOPIFY_API_VERSION}/products.json"
    params = {"status": "active", "limit": SHOPIFY_PRODUCTS_LIMIT}

    all_products: List[dict] = []
    seen_next_urls = set()

    while True:
        resp = requests.get(url, params=params, headers=headers, timeout=30)

        if resp.status_code >= 400:
            raise RuntimeError(f"Shopify API error {resp.status_code}: {resp.text[:300]}")

        payload = resp.json()
        page_products = payload.get("products", [])
        all_products.extend(page_products)

        # Debug
        #print(f"[Shopify] page fetched: {len(page_products)} | total: {len(all_products)}")

        # Shopify pagination
        next_link = resp.links.get("next")
        if not next_link:
            break

        next_url = next_link.get("url")
        if not next_url:
            break

        # Guard anti-loop
        if next_url in seen_next_urls:
            #print("[Shopify] WARNING: next_url repeated -> breaking to avoid infinite loop")
            break
        seen_next_urls.add(next_url)

        # From second page on
        url = next_url
        params = None  # next_url already contains all parameters

    return all_products





