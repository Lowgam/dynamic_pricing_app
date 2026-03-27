# Module chart_data_builder.py
# Purpose : build data for dashboard

from datetime import datetime, timedelta, timezone
from collections import defaultdict
import requests
from app.database.queries import get_latest_shopify_connection, get_products_by_ids

SHOPIFY_API_VERSION = "2026-01"
ORDERS_CACHE = None
ORDERS_CACHE_TIME = None

# ---------------------------------------------------
# Fx: API call and data request
# ---------------------------------------------------
def fetch_orders_last_days(shop_domain: str, access_token: str, days: int = 14):
    global ORDERS_CACHE, ORDERS_CACHE_TIME
    now = datetime.now(timezone.utc)

    # ---------------------------------------------------
    # 1) CACHE CHECK (5 minuti)
    # ---------------------------------------------------
    if ORDERS_CACHE is not None and ORDERS_CACHE_TIME is not None:
        if (now - ORDERS_CACHE_TIME).seconds < 300:
            print("[ORDERS] Using cache")
            return ORDERS_CACHE

    # ---------------------------------------------------
    # 2) Build request
    # ---------------------------------------------------
    date_min = (now - timedelta(days=days)).isoformat()

    headers = {
        "X-Shopify-Access-Token": access_token
    }

    url = f"https://{shop_domain}/admin/api/{SHOPIFY_API_VERSION}/orders.json"
    params = {
        "status": "any",
        "created_at_min": date_min,
        "limit": 250
    }

    all_orders = []
    seen_urls = set()

    # ---------------------------------------------------
    # 3) Pagination loop
    # ---------------------------------------------------
    while True:
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code >= 400:
            raise RuntimeError(
                f"Shopify API error {response.status_code}: {response.text[:200]}"
            )

        payload = response.json()
        orders = payload.get("orders", [])
        all_orders.extend(orders)

        print(f"[ORDERS] fetched {len(orders)} | total {len(all_orders)}")

        # Pagination
        next_link = response.links.get("next")
        if not next_link:
            break

        next_url = next_link.get("url")
        if not next_url:
            break

        if next_url in seen_urls:
            break
        seen_urls.add(next_url)

        url = next_url
        params = None

    # ---------------------------------------------------
    # 4) SAVE CACHE
    # ---------------------------------------------------
    ORDERS_CACHE = all_orders
    ORDERS_CACHE_TIME = now

    return all_orders
# ---------------------------------------------------
# Fx: Build data for chart
# ---------------------------------------------------
def build_daily_sales_map(orders, product_id: int):
    sales_per_day = defaultdict(int)

    for order in orders:
        # Extract date (only day part)
        created_at = order.get("created_at")
        if not created_at:
            continue

        day = created_at[:10]  # "YYYY-MM-DD"

        # Loop products inside order
        for item in order.get("line_items", []):
            if item.get("product_id") == product_id:
                quantity = item.get("quantity", 0)

                # Add to that day
                sales_per_day[day] += quantity

    print("DEBUG ORDER:", order.get("created_at"))

    for item in order.get("line_items", []):
        print("ITEM:", item.get("product_id"), "QTY:", item.get("quantity"))

    return sales_per_day

# ---------------------------------------------------
# Fx: Build data for chart
# ---------------------------------------------------
def build_chart_data(product_id: int) -> dict:
    from datetime import datetime, timedelta

    # ---------------------------------------------------
    # 0) Get Shopify connection
    # ---------------------------------------------------
    conn = get_latest_shopify_connection()
    if not conn:
        return {"labels": [], "values": []}

    shop_domain = conn["shop_domain"]
    access_token = conn["access_token"]

    # ---------------------------------------------------
    # 1) Get product and Shopify ID
    # ---------------------------------------------------
    product_list = get_products_by_ids([product_id])
    if not product_list:
        return {"labels": [], "values": []}

    product = product_list[0]
    shopify_id = product["shopify_id"]

    # ---------------------------------------------------
    # 2) Fetch orders
    # ---------------------------------------------------
    orders = fetch_orders_last_days(
        shop_domain,
        access_token,
        days=14
    )

    # ---------------------------------------------------
    # 3) Aggregate sales per day
    # ---------------------------------------------------
    sales_map = {}

    for order in orders:
        created_at = order.get("created_at")
        if not created_at:
            continue

        day = created_at[:10]  # YYYY-MM-DD

        if day not in sales_map:
            sales_map[day] = 0

        for item in order.get("line_items", []):
            if item.get("product_id") == shopify_id:
                quantity = item.get("quantity", 0)
                sales_map[day] += quantity

    print("DEBUG SALES MAP:", sales_map)

    # ---------------------------------------------------
    # 4) Build full 14-day series
    # ---------------------------------------------------
    labels = []
    values = []

    today = datetime.now().date()

    for i in range(14):
        day = today - timedelta(days=(13 - i))
        day_str = day.strftime("%Y-%m-%d")

        labels.append(day.strftime("%d-%m"))
        values.append(sales_map.get(day_str, 0))

    # ---------------------------------------------------
    # 5) Return chart format
    # ---------------------------------------------------
    return {
        "product_id": product_id,
        "labels": labels,
        "values": values,
    }