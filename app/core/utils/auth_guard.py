# Module : auth_guard.py
# Purpose : control if exists already a request.session (cookie). If not -> go to /login

from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi import HTTPException

def require_login(request: Request):
    if not request.session.get("user_id"):
        raise HTTPException(
            status_code=303,
            headers={"Location": "/login"},
        )
    return None
