# Module : auth_guard.py
# Purpose : control if exists already a request.session (cookie). If not -> go to /login

from fastapi import Request, HTTPException

def require_login(request: Request):
    if not request.session.get("user_id"):
        raise HTTPException(
            status_code=303,
            headers={"Location": "/login"},
        )
    return None

# Dictionary key - value
ROLE_HIERARCHY = {
    "user": 1,
    "admin": 2,
    "dev": 3,
}

def require_role(min_role: str):
    def _guard(request: Request):
        role = request.session.get("role")

        if not role:
            raise HTTPException(
                status_code=303,
                headers={"Location": "/login"}
            )

        if ROLE_HIERARCHY.get(role, 0) < ROLE_HIERARCHY[min_role]:
            raise HTTPException(
                status_code=303,
                headers={"Location": "/dashboard"}
            )
    return _guard