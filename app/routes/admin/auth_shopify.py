# Module: auth_shopify.py
# Purpose: authentication shopify, OAuth routes

import os
import secrets
import urllib.parse

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.core.utils.auth_guard import require_login

router = APIRouter(
    dependencies=[Depends(require_login)]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/shopify/connect", response_class=HTMLResponse)
def shopify_connect(request: Request):
    SHOP = os.getenv("SHOPIFY_SHOP_DOMAIN")          # es: sirplus-food.myshopify.com
    CLIENT_ID = os.getenv("SHOPIFY_CLIENT_ID")
    REDIRECT_URI = os.getenv("SHOPIFY_REDIRECT_URI") # es: https://xxxx.ngrok-free.dev/auth/shopify/callback
    SCOPES = os.getenv("SHOPIFY_SCOPES", "read_products,read_inventory,read_orders")

    if not SHOP or not CLIENT_ID or not REDIRECT_URI:
        raise RuntimeError("Missing env vars: SHOPIFY_SHOP_DOMAIN / SHOPIFY_CLIENT_ID / SHOPIFY_REDIRECT_URI")

    state = secrets.token_urlsafe(16)
    request.session["shopify_oauth_state"] = state

    params = {
        "client_id": CLIENT_ID,
        "scope": SCOPES,
        "redirect_uri": REDIRECT_URI,
        "state": state,
    }
    authorize_url = f"https://{SHOP}/admin/oauth/authorize?{urllib.parse.urlencode(params)}"
    return RedirectResponse(authorize_url)