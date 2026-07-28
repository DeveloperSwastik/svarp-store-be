"""
Auth API routes — login, register, profile management, and OTP verification.
Delegates user operations to user portal and email/OTP operations to email portal.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.schemas.auth import LoginRequest, RegisterRequest, OTPGenerateSchema, OTPVerifySchema
from app.services.auth_service import auth_service
from app.clients.email_client import email_client
from app.middleware.auth import get_current_user
from app.clients.base import ServiceError

logger = logging.getLogger("store-bff")

router = APIRouter(prefix="/auth", tags=["auth"])


async def _send_welcome_email_task(to_email: str, full_name: str):
    """Background task to dispatch welcome email via portal-email service."""
    try:
        await email_client.send_templated_email(
            template_slug="welcome-email",
            to_email=to_email,
            to_name=full_name,
            variables={
                "user_name": full_name or to_email.split("@")[0],
                "login_url": "https://store.svarp.org/login",
            },
        )
        logger.info(f"Welcome email dispatched successfully for {to_email}")
    except Exception as e:
        logger.error(f"Failed to dispatch welcome email for {to_email}: {e}")


@router.post("/login")
async def login(request: LoginRequest):
    """Authenticate user via user portal and return store JWT."""
    try:
        return await auth_service.login(request.email, request.password)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/signup")
async def register(request: RegisterRequest, background_tasks: BackgroundTasks):
    """Register new user via user portal after OTP verification, auto-login, and dispatch welcome email in background."""
    if not request.otp_code:
        raise HTTPException(status_code=400, detail="OTP verification code is required for signup")

    try:
        verify_res = await email_client.verify_otp(
            identifier=request.email,
            otp_code=request.otp_code,
            purpose="signup"
        )
        if not verify_res.get("verified"):
            raise HTTPException(status_code=400, detail=verify_res.get("message", "Invalid or expired OTP code"))

        res = await auth_service.register(request.email, request.password, request.full_name)
        background_tasks.add_task(_send_welcome_email_task, request.email, request.full_name)
        return res
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/otp/send")
async def send_otp(request: OTPGenerateSchema):
    """Generate & send numeric OTP code via portal-email service."""
    try:
        return await email_client.generate_otp(
            identifier=request.email,
            purpose=request.purpose,
            app_name="SVARP Store",
            template_slug="otp-verification"
        )
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/otp/verify")
async def verify_otp(request: OTPVerifySchema):
    """Verify numeric OTP code via portal-email service and return store JWT if verified."""
    try:
        verify_res = await email_client.verify_otp(
            identifier=request.email,
            otp_code=request.otp_code,
            purpose=request.purpose
        )
        if not verify_res.get("verified"):
            raise HTTPException(status_code=400, detail=verify_res.get("message", "Invalid or expired OTP code"))

        return await auth_service.otp_login(request.email)
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
