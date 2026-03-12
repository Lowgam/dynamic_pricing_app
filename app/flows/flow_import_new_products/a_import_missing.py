# Module : import_missing.py
# Purpose : endpoint import-missing

from fastapi import APIRouter, Depends
from starlette.responses import RedirectResponse


from app.adapters.shopify.mapper import map_shopify_product_to_db
from app.core.services.product_importer import import_missing_products
from app.core.utils.auth_guard import require_login
from app.database.queries import get_latest_shopify_connection
from app.flows.flow_import_new_products.b_import_missing_products import fetch_active_products_from_shopify

router = APIRouter(
    dependencies=[Depends(require_login)]
)

@router.post("/admin/import-missing")
def admin_import_missing_products():
    # 1) Read shop_domain and token from DB
    conn = get_latest_shopify_connection()
    if not conn:
        return RedirectResponse(url="/admin?imported=0&error=no_shopify_connection", status_code=303)
    shop_domain = conn["shop_domain"]
    access_token = conn["access_token"]

    # 2) Fetch products from Shopify
    try:
        shopify_products = fetch_active_products_from_shopify(shop_domain, access_token)
        #print(f"[Shopify] products fetched (total): {len(shopify_products)}")

    except Exception as e:
        #print(f"[Shopify] fetch failed: {e}")
        return RedirectResponse(url="/admin?imported=0&error=shopify_fetch_failed", status_code=303)

    # 3) Map Shopify -> internal DB model
    internal_products = []
    for p in shopify_products:
        if p.get("status") == "active":
            internal_products.append(map_shopify_product_to_db(p))

    # 4) Import missing products into DB
    imported_count = import_missing_products(internal_products)
    #print(f"[Import] imported_count={imported_count} out of fetched={len(shopify_products)}")

    # 5) Response
    return RedirectResponse (url=f"/admin?imported={imported_count}", status_code=303)

