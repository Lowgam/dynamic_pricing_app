# Module : import_missing_products.py
# Purpose : create endpoint for admin to import missing products.

import json
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse

from app.adapters.shopify.mapper import map_shopify_product_to_db
from app.core.services.product_importer import import_missing_products

router = APIRouter()

@router.post("/admin/import-missing")
def admin_import_missing_products():
    # 1) Import MOCK JSON
    # Reading a file. r means read. as f means close it when finished.
    with open ("data/samples/product_shopify_mock.json", "r") as f:
        # Converts a json in a py dict. Why dict? Because dict and JSON are basically the same thing.
        # The fx recognize that is a dict and creates one.
        payload = json.load(f)

    shopify_products = payload.get("products", [])

    # 2) Map shopify products to -> DB map
    internal_products = []
    for p in shopify_products:
        if p.get("status") == "active":
            mapped_p = map_shopify_product_to_db(p)
            internal_products.append(mapped_p)

    # 3) Import missing
    imported_count = import_missing_products(internal_products)

    # 4) Response
    return RedirectResponse(
        url=f"/admin?imported={imported_count}",
        status_code=303
    )

