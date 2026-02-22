from fastapi import APIRouter, HTTPException
from schemas.admin import AdminRegister, AdminLogin
from services.admin_service import register_admin, login_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/register")
def register(data: AdminRegister):
    try:
        return register_admin(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(data: AdminLogin):
    try:
        return login_admin(data)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))