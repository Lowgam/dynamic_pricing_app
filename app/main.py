from fastapi import FastAPI,Request
from app.routes import products, pricing, ui, dashboard
from app.routes.admin import admin, weights, sync
from fastapi.templating import Jinja2Templates

# creation app, FastAPI() = constructor. Everything I am going to add is going to be attached to this object
# In py I can create variables without specifying the nature. In this case we take an object from FastAPI library
app = FastAPI()
template = Jinja2Templates(directory="app/templates")

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
app.include_router(products.router)

# -------------------------------------------------------
# Endpoint for JSON
# -------------------------------------------------------
app.include_router(pricing.router)

# -------------------------------------------------------
# Endpoint for UI
# -------------------------------------------------------
app.include_router(ui.router)

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
# Endpoint for /admin/sync
# -------------------------------------------------------
app.include_router(sync.router)