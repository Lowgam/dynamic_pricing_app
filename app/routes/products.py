# Module : products.py
# Purpose : connecting FastAPI with the DB. Returning a JSON list.Tr

#APIRouter needed for routing system.
from fastapi import APIRouter, Request
from app.database.queries import get_all_products
# jinja2 deals with the creation of the HTML part, because FastAPI can only give JSON responses. Without jinja2 we should
# write HTML strings with python (not suggested) or use a separated front end, for example React.
from fastapi.templating import Jinja2Templates

# Router creation. It is a fastapi class, it is needed to define endpoint and attach this endpoint ot the main,py.
# the router object itself it is empty, we need its ability to connect the main.py
router = APIRouter()

# A template is an HTML file with a placeholder that will be used by jinja2 by knowing where to fullfill lacks
# In this way we are able to separate py logic to HTML/CSS
templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------
# Fx: Get all products to endpoint : JSON
# ---------------------------------------------------
# Endpoint definition. When this endpoint is called, the following function is executed.
@router.get("/products")
async def list_products():
    products = get_all_products()
    # We can ask to return a dict. FastAPI is able (as said before) to translate the datas in a flexible way.
    # In this case we say: we need the datas formatted as this dict.
    return {"products": products}