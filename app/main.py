from fastapi import FastAPI
from app.routes import products

# creation app, FastAPI() = constructor. Everything I am going to add is going to be attached to this object
# In py I can create variables without specifying the nature. In this case we take an object from FastAPI library
app = FastAPI()

# decorator. Goes before the function. Is used to modify a function before is activation.
# In this case FastAPI use a decorator to associate a function to an endpoint (server's address that answers clients requests)
# GET request comes from HTTP methods. Get = data requests, POST = send datas to server, PUT = update, DELETE = cancel
# Here: if someone makes a GET request to this endpoint -> run function home()
# Why ("/")? Because in a webpage / means homepage. It is possible to use it in different sections, for example /login
@app.get("/")
# with def I can define functions
def home():
    return {"message": "Dynamic Pricing App - Server is active!!!"}

app.include_router(products.router)