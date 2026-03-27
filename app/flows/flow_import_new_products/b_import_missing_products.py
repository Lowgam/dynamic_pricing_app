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

        for p in page_products:
            product_id = p["id"]

            expiry_date = fetch_product_expiry_date(shop_domain, access_token, product_id)
            if expiry_date:
                if "metafields" not in p:
                    p["metafields"] = {}

                p["metafields"]["expiry_date"] = expiry_date

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

def fetch_product_expiry_date(
        shop_domain: str,
        access_token: str,
        product_id: int,
) -> Optional[str]:
    url = f"https://{shop_domain}/admin/api/{SHOPIFY_API_VERSION}/products/{product_id}/metafields.json"
    headers = {"X-Shopify-Access-Token": access_token}

    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code >= 400:
        return None

    payload = resp.json()
    metafields = payload.get("metafields", [])

    for mf in metafields:
        if mf.get("namespace") == "custom" and mf.get("key") == "mhd":
            return mf["value"]

    return None


