"""
Request/response schemas for auth endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = Field(..., min_length=2, max_length=100)
    otp_code: Optional[str] = Field(None, min_length=6, max_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    roles: List[str] = []


class OTPGenerateSchema(BaseModel):
    email: EmailStr
    purpose: str = "login"


class OTPVerifySchema(BaseModel):
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    purpose: str = "login"
