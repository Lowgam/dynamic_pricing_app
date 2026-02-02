# Module: shopify_oauth.py
# Purpose: Shopify OAuth callback (exchanges code -> access_token)

import os
import hmac
import hashlib
import requests

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database.db import get_connection

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _verify_shopify_hmac(query_params, client_secret: str) -> bool:
    received_hmac = query_params.get("hmac")
    if not received_hmac:
        return False

    items = []
    for k, v in query_params.multi_items():
        if k in ("hmac", "signature"):
            continue
        items.append((k, v))

    items.sort(key=lambda x: x[0])
    message = "&".join(f"{k}={v}" for k, v in items)

    digest = hmac.new(
        client_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(digest, received_hmac)


def save_shopify_token(shop: str, access_token: str, scopes: str | None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO shopify_connections (shop_domain, access_token, scopes)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                access_token = VALUES(access_token),
                scopes = VALUES(scopes)
            """,
            (shop, access_token, scopes),
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


@router.get("/auth/shopify/callback", response_class=HTMLResponse)
def shopify_callback(
    request: Request,
    code: str | None = None,
    shop: str | None = None,
    state: str | None = None,
):
    DEBUG = "CALLBACK_V3"

    client_id = os.getenv("SHOPIFY_CLIENT_ID")
    client_secret = os.getenv("SHOPIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        return templates.TemplateResponse(
            "shopify_callback.html",
            {
                "request": request,
                "ok": False,
                "message": f"[{DEBUG}] Missing Shopify credentials",
                "data": {},
            },
        )

    if not code or not shop or not state:
        return templates.TemplateResponse(
            "shopify_callback.html",
            {
                "request": request,
                "ok": False,
                "message": f"[{DEBUG}] Missing code / shop / state",
                "data": dict(request.query_params),
            },
        )

    expected_state = request.session.get("shopify_oauth_state")
    if state != expected_state:
        return templates.TemplateResponse(
            "shopify_callback.html",
            {
                "request": request,
                "ok": False,
                "message": f"[{DEBUG}] Invalid state",
                "data": {"expected": expected_state, "received": state},
            },
        )

    request.session.pop("shopify_oauth_state", None)

    if not _verify_shopify_hmac(request.query_params, client_secret):
        return templates.TemplateResponse(
            "shopify_callback.html",
            {
                "request": request,
                "ok": False,
                "message": f"[{DEBUG}] HMAC validation failed",
                "data": {},
            },
        )

    # ---- TOKEN EXCHANGE ----
    token_url = f"https://{shop}/admin/oauth/access_token"

    r = requests.post(
        token_url,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
        },
        timeout=20,
    )

    if r.status_code != 200:
        return templates.TemplateResponse(
            "shopify_callback.html",
            {
                "request": request,
                "ok": False,
                "message": f"[{DEBUG}] Token exchange failed",
                "data": r.text,
            },
        )

    payload = r.json()
    access_token = payload.get("access_token")
    scopes = payload.get("scope")

    if not access_token:
        return templates.TemplateResponse(
            "shopify_callback.html",
            {
                "request": request,
                "ok": False,
                "message": f"[{DEBUG}] access_token missing",
                "data": payload,
            },
        )

    # ---- SAVE IN DB (QUI, UNA SOLA VOLTA, FINE) ----
    try:
        save_shopify_token(shop, access_token, scopes)
    except Exception as e:
        return templates.TemplateResponse(
            "shopify_callback.html",
            {
                "request": request,
                "ok": False,
                "message": f"[{DEBUG}] DB save failed",
                "data": str(e),
            },
        )

    masked = access_token[:6] + "..." + access_token[-4:]

    return templates.TemplateResponse(
        "shopify_callback.html",
        {
            "request": request,
            "ok": True,
            "message": f"[{DEBUG}] Shopify connected ✅ Token saved",
            "data": {
                "shop": shop,
                "scopes": scopes,
                "access_token_masked": masked,
            },
        },
    )
