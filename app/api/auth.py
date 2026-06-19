"""
Auth API routes — login, register, profile management.
Delegates all user operations to the user portal microservice.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import auth_service
from app.middleware.auth import get_current_user
from app.clients.base import ServiceError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(request: LoginRequest):
    """Authenticate user via user portal and return store JWT."""
    try:
        return await auth_service.login(request.email, request.password)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/signup")
async def register(request: RegisterRequest):
    """Register new user via user portal, auto-login, return store JWT."""
    try:
        return await auth_service.register(request.email, request.password, request.full_name)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/me")
async def get_me(user: dict = Depends(get_current_user)):
    """Return current user profile from user portal."""
    try:
        profile = await auth_service.get_profile(user.get("sub"))
        return profile
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put("/profile")
async def update_profile(data: dict, user: dict = Depends(get_current_user)):
    """Update user profile via user portal."""
    try:
        return await auth_service.update_profile(user.get("sub"), data)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/me/address")
async def get_address(user: dict = Depends(get_current_user)):
    """Fetch current user's saved address from the user portal."""
    try:
        return await auth_service.get_address(user.get("sub"))
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/me/address")
async def update_address(data: dict, user: dict = Depends(get_current_user)):
    """Save or update current user's address in the user portal."""
    try:
        return await auth_service.update_address(user.get("sub"), data)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
