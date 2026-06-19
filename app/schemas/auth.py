"""
Request/response schemas for auth endpoints.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    roles: List[str] = []
