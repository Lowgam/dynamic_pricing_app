from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from app.core.services.product_check import count_missing_active_products
from app.core.utils.auth_guard import require_login, require_role
from app.core.services.user_service import register_user, delete_user
from app.database.queries import get_all_users
from app.core.services.events_service import has_events_to_sync

router = APIRouter(
    dependencies=[Depends(require_role("admin"))]
)
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin")
async def admin_dashboard(request: Request):
    missing_products = count_missing_active_products()
    users = get_all_users()
    events_to_sync = has_events_to_sync()
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "missing_products": missing_products,
            "users": users,
            "events_to_sync": events_to_sync
        }
    )

@router.post("/admin/users/create")
async def create_user_admin(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        role: str = Form("user"),
):
    register_user(username, password, role=role)
    return RedirectResponse("/admin?user_created=1", status_code=303)

@router.post("/admin/users/delete")
async def delete_user_admin(
        user_id: int = Form(...),
):
    if user_id != 1:
        delete_user(user_id)

    return RedirectResponse("/admin?user_delete=1", status_code=303)