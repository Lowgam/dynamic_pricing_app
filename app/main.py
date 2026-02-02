from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routes import dashboard, auth, shopify_oauth
from app.routes.admin import admin, weights, events_sync, train, sv_sync, reset, import_missing_products, clear_products, auth_shopify
from dotenv import load_dotenv

# creation app, FastAPI() = constructor. Everything I am going to add is going to be attached to this object
# In py I can create variables without specifying the nature. In this case we take an object from FastAPI library
app = FastAPI()

# Allow our program to read .env for Shopify connection
load_dotenv()

# Allows FastAPI to have a session for every user, through saving cookies for every user
# We need it here to do not ask password at every page.
# A cookie is a small text file that the server ask the browser to keep. It is needed because HTTP has no memory.
# The server doesn't know you are the same user. With cookies the server recognise browser and saved info.
# A cookie is signed with a secret_key to verify it.
app.add_middleware(
    SessionMiddleware,
    secret_key="CHANGE_ME_SECRET_KEY",
)
template = Jinja2Templates(directory="app/templates")

# FastAPI needs to mount static files like css.
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# decorator. Goes before the function. Is used to modify a function before is activation.
# In this case FastAPI use a decorator to associate a function to an endpoint (server's address that answers clients requests)
# GET request comes from HTTP methods. Get = data requests, POST = send datas to server, PUT = update, DELETE = cancel
# Here: if someone makes a GET request to this endpoint -> run function home()
# Why ("/")? Because in a webpage / means homepage. It is possible to use it in different sections, for example /login
@app.get("/")
# with def I can define functions
# -------------------------------------------------------
# Endpoint / (home)
# -------------------------------------------------------
def home(Request: Request):
    return template.TemplateResponse(
        "home.html",
        {"request": Request,}
    )

# -------------------------------------------------------
# Endpoint /products or /products-ui
# -------------------------------------------------------
#app.include_router(products.router)

# -------------------------------------------------------
# Endpoint for JSON
# -------------------------------------------------------
#app.include_router(pricing.router)

# -------------------------------------------------------
# Endpoint for UI
# -------------------------------------------------------
#app.include_router(ui.router)

# -------------------------------------------------------
# Endpoint for /dashboard
# -------------------------------------------------------
app.include_router(dashboard.router)

# -------------------------------------------------------
# Endpoint for /admin
# -------------------------------------------------------
app.include_router(admin.router)

# -------------------------------------------------------
# Endpoint for /admin/weights
# -------------------------------------------------------
app.include_router(weights.router)

# -------------------------------------------------------
# Endpoint for /admin/events_sync
# -------------------------------------------------------
app.include_router(events_sync.router)

# -------------------------------------------------------
# Endpoint for /admin/train
# -------------------------------------------------------
app.include_router(train.router)

# -------------------------------------------------------
# Endpoint for /admin/sv_sync
# -------------------------------------------------------
app.include_router(sv_sync.router)

# -------------------------------------------------------
# Endpoint for /admin/reset
# -------------------------------------------------------
app.include_router(reset.router)

# -------------------------------------------------------
# Endpoint for /admin/import-missing
# -------------------------------------------------------
app.include_router(import_missing_products.router)

# -------------------------------------------------------
# Endpoint for /admin/clear-products
# -------------------------------------------------------
app.include_router(clear_products.router)

# -------------------------------------------------------
# Endpoint for /login
# -------------------------------------------------------
app.include_router(auth.router)

# -------------------------------------------------------
# Endpoint for /shopify/connect
# -------------------------------------------------------
app.include_router(auth_shopify.router, prefix="/admin")

# -------------------------------------------------------
# Endpoint for /auth/shopify/callback
# -------------------------------------------------------
app.include_router(shopify_oauth.router)