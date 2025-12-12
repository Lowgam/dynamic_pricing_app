from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin")
async def admin_dashboard(request: Request):
    return templates.TemplateResponse(
        "admin.html",
        {"request": request}
    )
