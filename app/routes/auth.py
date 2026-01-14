# Module : auth.py
# Purpose :

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database.queries import get_user_by_username
from app.core.utils.security import verify_password

router = APIRouter()
templates = Jinja2Templates("app/templates")

@router.post("/login")
async def login(
        request: Request,
        # Important FastAPI syntax: FastAPI extract from the HTML form the right values (username,password)
        # and give it to the FX
        username: str = Form(...),
        password: str = Form(...),
):
    user = get_user_by_username(username)

    if not user:
        return RedirectResponse("/login?error=invalid", status_code=303)

    if not verify_password(password, user["password_hash"]):
        return RedirectResponse("/login?error=invalid", status_code=303)

    request.session["user_id"] = user["id"]
    request.session["role"] = user["role"]

    return RedirectResponse("/", status_code=303)

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

@router.get("/logout")
async def logout_page(request: Request, confirm: int | None = None):
    if confirm:
        request.session.clear()
        return RedirectResponse("/login", status_code=303)
    
    return templates.TemplateResponse(
        "logout.html",
        {"request": request}
    )